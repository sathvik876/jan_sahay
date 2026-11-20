# backend/app/api.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from . import db, models, schemas, rag, eligibility
import os

router = APIRouter()

@router.post("/chat")
async def chat(request: schemas.ChatRequest, db: Session = Depends(db.get_db)):
    answer = await rag.generate_answer(request.message, request.language)
    schemes = []
    seen_names = set()
    for scheme in db.query(models.Scheme).order_by(models.Scheme.id).all():
        if scheme.name not in seen_names:
            seen_names.add(scheme.name)
            schemes.append(scheme)
        if len(schemes) == 6:
            break
    return {
        "answer": answer,
        "schemes": [schemas.SchemeOut.from_orm(scheme) for scheme in schemes],
    }

@router.post("/schemes/search")
def search_schemes(req: schemas.SchemeSearchRequest, db: Session = Depends(db.get_db)):
    # Basic filter by state/category – more advanced RAG is in /chat
    q = db.query(models.Scheme)
    if req.state:
        q = q.filter(models.Scheme.state == req.state)
    if req.category:
        q = q.filter(models.Scheme.category == req.category)
    results = q.limit(20).all()
    return [schemas.SchemeOut.from_orm(s) for s in results]

@router.post("/eligibility/check")
def check_eligibility(req: schemas.EligibilityCheckRequest, db: Session = Depends(db.get_db)):
    result = eligibility.evaluate(req.scheme_id, req.user_data, db)
    return result

@router.post("/documents/analyze")
async def analyze_document(file: UploadFile = File(...)):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Files must be 10 MB or smaller.")

    content_type = file.content_type or ""
    if content_type == "application/pdf" or (file.filename or "").lower().endswith(".pdf"):
        try:
            text = rag.extract_text(contents)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="No selectable text was found. Scanned PDFs need OCR; upload a text-based PDF or a clear image instead.",
            )
        summary = await rag.summarize_document(text)
        return {"summary": summary, "text": text[:500]}

    if content_type.startswith("image/"):
        try:
            summary = await rag.summarize_image(contents, content_type)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {"summary": summary, "text": ""}

    raise HTTPException(status_code=415, detail="Upload a PDF or an image file.")

@router.get("/health")
def health_check():
    return {"status": "ok"}
