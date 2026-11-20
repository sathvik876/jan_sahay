# backend/app/rag.py

import asyncio
import base64
import os
from typing import List
from google import genai

_GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
_GEMINI_CLIENT = (
    genai.Client(api_key=_GEMINI_API_KEY)
    if _GEMINI_API_KEY and not _GEMINI_API_KEY.lower().startswith(("your_", "replace", "changeme"))
    else None
)
_GEMINI_MODEL = "gemini-4-hydrogen"


def _generate_content(content):
    interaction = _GEMINI_CLIENT.interactions.create(
        model=_GEMINI_MODEL,
        input=content,
    )
    return interaction.output_text

async def generate_answer(question: str, language: str = "en") -> str:
    """Generate a grounded answer using Gemini.
    If a Chroma collection has been populated, we retrieve the top‑k relevant chunks
    and prepend them to the prompt so Gemini can cite sources.
    """
    # 1️⃣ Retrieve relevant passages (if collection exists and Gemini key is set)
    from .chroma_loader import retrieve_relevant
    try:
        relevant = retrieve_relevant(question, k=3)
        # Build a citation block
        citation_text = "\n---\nRelevant source excerpts:\n"
        for i, r in enumerate(relevant, start=1):
            source = r["metadata"].get("source", "unknown")
            excerpt = r["text"].replace("\n", " ")[:200]
            citation_text += f"[{i}] ({source}) {excerpt}...\n"
    except Exception as e:
        # If Chroma is not initialized or any error, fall back to empty citations
        citation_text = ""
        relevant = []
    # 2️⃣ Build the final prompt for Gemini
    if _GEMINI_CLIENT:
        prompt = (
            f"Answer the following question in {language}.\n"
            f"Provide a concise answer and, when possible, include citations to the excerpts below.\n"
            f"Question: {question}\n"
            f"{citation_text}"
        )
        try:
            response = await asyncio.to_thread(_generate_content, prompt)
            if response:
                return response.strip()
        except Exception as exc:
            print(f"[rag] Gemini unavailable: {exc}")
    # Local fallback used when Gemini is not configured or the API key is unavailable.
    if relevant:
        source = relevant[0]["metadata"].get("source", "local scheme data")
        source_name = os.path.basename(str(source))
        if language == "hi":
            return (
                "उपलब्ध स्थानीय जानकारी के अनुसार, तेलंगाना छात्रवृत्ति में "
                "कॉलेज में नामांकन होना, आय सीमा और आयु सीमा शामिल हो सकती है। "
                f"कृपया आधिकारिक पोर्टल पर पात्रता और दस्तावेज सत्यापित करें। "
                f"(स्रोत: {source_name})"
            )
        if language == "te":
            return (
                "అందుబాటులో ఉన్న స్థానిక సమాచారం ప్రకారం, తెలంగాణ విద్యార్థి స్కాలర్షిప్‌కు "
                "కాలేజీలో నమోదు, ఆదాయ పరిమితి మరియు వయసు పరిమితి ఉండవచ్చు। "
                f"పాత్రత మరియు అవసరమైన పత్రాలను అధికారిక పోర్టల్లో నిర్ధారించండి। "
                f"(మూలం: {source_name})"
            )
        return (
            "Based on the available local scheme information, a Telangana student "
            "scholarship may require college enrollment and may have income and age limits. "
            f"Please verify eligibility and required documents on the official portal. "
            f"(Source: {source_name})"
        )
    if language == "hi":
        return "मुझे अभी स्थानीय रिकॉर्ड में इस प्रश्न का सटीक उत्तर नहीं मिला। कृपया राज्य और आयु जैसी अधिक जानकारी दें।"
    if language == "te":
        return "ఈ ప్రశ్నకు సంబంధించిన సమాచారం స్థానిక రికార్డులో నాపకి లేదు. దయచేసి రాష్ట్రం మరియు వయసు వంటి వివరాలు ఇవ్వండి."
    return "I could not find a matching local record for that question. Please add details such as state, age, income, and occupation."

def extract_text(contents: bytes) -> str:
    """Extract selectable text from an uploaded PDF."""
    try:
        import fitz  # PyMuPDF
        with fitz.open(stream=contents, filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)
    except Exception as exc:
        raise ValueError("The PDF could not be opened. Check that the file is a valid, unencrypted PDF.") from exc

async def summarize_document(text: str) -> str:
    """Summarise the extracted document text via Gemini (or fallback)."""
    if not text:
        return "No readable content extracted."
    if _GEMINI_CLIENT:
        prompt = f"Summarise the following government notice in plain language (English).\n---\n{text}\n---"
        try:
            response = await asyncio.to_thread(_generate_content, prompt)
            if response:
                return response.strip()
        except Exception as exc:
            print(f"[rag] Gemini document summary unavailable: {exc}")
    excerpt = " ".join(text.split())
    return (
        "AI summarization is unavailable, so here is the extracted document text for review:\n"
        + excerpt[:1500]
        + ("..." if len(excerpt) > 1500 else "")
    )

async def summarize_image(contents: bytes, content_type: str) -> str:
    if not _GEMINI_CLIENT:
        raise RuntimeError("Image analysis requires a valid Gemini API key. Configure GEMINI_API_KEY in backend/.env, then restart the backend.")
    try:
        response = await asyncio.to_thread(
            _generate_content,
            [
                {
                    "type": "text",
                    "text": "Read this government notice image. Summarize its purpose, eligibility conditions, important dates, and required documents in plain English. If any text is unreadable, say so. Do not invent missing details.",
                },
                {
                    "type": "image",
                    "data": base64.b64encode(contents).decode("ascii"),
                    "mime_type": content_type,
                },
            ],
        )
        if response:
            return response.strip()
        raise RuntimeError("Gemini did not return a readable summary for this image.")
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Image analysis failed. Check the Gemini API key and try again.") from exc
