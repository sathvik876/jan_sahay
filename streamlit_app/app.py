import mimetypes
import os

import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


st.set_page_config(
    page_title="JanSahay AI | Citizen Assistance",
    page_icon="🇮🇳",
    layout="wide",
)


def get_api_base_url() -> str:
    fallback = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    try:
        return str(st.secrets.get("API_BASE_URL", fallback)).rstrip("/")
    except StreamlitSecretNotFoundError:
        return fallback.rstrip("/")


API_BASE_URL = get_api_base_url()

st.markdown(
    """
    <style>
    .block-container { max-width: 1100px; padding-top: 2rem; }
    [data-testid="stSidebar"] { background: #f5f8fc; }
    .hero {
        padding: 1.7rem 2rem;
        margin-bottom: 1.2rem;
        border-radius: 16px;
        color: white;
        background: linear-gradient(110deg, #173b70, #3479bd);
    }
    .hero h1 { margin: 0 0 .35rem; color: white; font-size: 2rem; }
    .hero p { margin: 0; color: #e2efff; }
    .small-note { color: #68778a; font-size: .88rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_request(method: str, path: str, **kwargs):
    timeout = kwargs.pop("timeout", 90)
    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{path}",
            timeout=timeout,
            **kwargs,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not reach the backend at {API_BASE_URL}. "
            "Check that the API is deployed and API_BASE_URL is set correctly."
        ) from exc

    try:
        payload = response.json()
    except ValueError:
        payload = {"detail": response.text[:500] or "The backend returned an unreadable response."}

    if not response.ok:
        detail = payload.get("detail", f"Backend returned HTTP {response.status_code}.")
        raise RuntimeError(str(detail))
    return payload


def load_schemes():
    schemes = api_request("POST", "/api/schemes/search", json={})
    if not isinstance(schemes, list):
        raise RuntimeError("The backend returned an invalid scheme list.")
    return schemes


def show_scheme_cards(schemes):
    if not schemes:
        st.info("No schemes match these filters.")
        return
    columns = st.columns(3)
    for index, scheme in enumerate(schemes):
        with columns[index % 3]:
            with st.container(border=True):
                st.subheader(scheme.get("name", "Government scheme"))
                st.caption(
                    " · ".join(
                        value
                        for value in (scheme.get("category"), scheme.get("state"))
                        if value
                    )
                    or "Category details not available"
                )
                if scheme.get("department"):
                    st.write(f"**Department:** {scheme['department']}")
                if scheme.get("status"):
                    st.write(f"**Status:** {scheme['status']}")
                st.caption("Verify current eligibility and documents with the official scheme authority.")


def send_chat(message: str, language: str):
    st.session_state.messages.append({"role": "user", "content": message})
    st.session_state.chat_error = ""
    try:
        with st.spinner("Looking for relevant information..."):
            result = api_request(
                "POST",
                "/api/chat",
                json={"message": message, "language": language},
            )
        answer = result.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("The backend returned an empty answer.")
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.chat_schemes = result.get("schemes", [])
    except RuntimeError as exc:
        st.session_state.chat_error = str(exc)
    st.rerun()


st.sidebar.title("JanSahay AI")
st.sidebar.caption("Citizen Assistance")
page = st.sidebar.radio(
    "Choose a service",
    ["AI Assistant", "Explore Schemes", "Check Eligibility", "Analyze Document"],
)

try:
    health = api_request("GET", "/api/health", timeout=5)
except RuntimeError as exc:
    st.sidebar.error("Backend unavailable")
    st.sidebar.caption(str(exc))
else:
    st.sidebar.success("Backend connected" if health.get("status") == "ok" else "Backend responded")

st.markdown(
    """
    <div class="hero">
      <h1>Government support, made simple.</h1>
      <p>Find schemes, check eligibility, and understand documents in your language.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "AI Assistant":
    st.subheader("JanSahay Assistant")
    language_options = {"English": "en", "हिन्दी": "hi", "తెలుగు": "te"}
    language_label = st.selectbox("Response language", list(language_options))

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_schemes" not in st.session_state:
        st.session_state.chat_schemes = []
    if "chat_error" not in st.session_state:
        st.session_state.chat_error = ""

    if st.sidebar.button("＋ New chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_schemes = []
        st.session_state.chat_error = ""
        st.rerun()

    if not st.session_state.messages:
        st.info("Ask about scholarships, pensions, farming schemes, or government services.")
        suggestion_columns = st.columns(3)
        suggestions = [
            "Which scholarships are available for students?",
            "What support is available for farmers?",
            "Tell me about pension schemes.",
        ]
        for column, suggestion in zip(suggestion_columns, suggestions):
            with column:
                if st.button(suggestion, use_container_width=True):
                    send_chat(suggestion, language_options[language_label])

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.chat_error:
        st.error(st.session_state.chat_error)
        last_user_message = next(
            (item["content"] for item in reversed(st.session_state.messages) if item["role"] == "user"),
            "",
        )
        if last_user_message and st.button("Retry last question"):
            st.session_state.messages.pop()
            send_chat(last_user_message, language_options[language_label])

    if st.session_state.chat_schemes:
        st.markdown("#### Suggested schemes")
        show_scheme_cards(st.session_state.chat_schemes)

    prompt = st.chat_input("Type your question...")
    if prompt:
        send_chat(prompt, language_options[language_label])

elif page == "Explore Schemes":
    st.subheader("Explore government schemes")
    try:
        schemes = load_schemes()
        categories = sorted({item.get("category") for item in schemes if item.get("category")})
        states = sorted({item.get("state") for item in schemes if item.get("state")})
        filters = st.columns([2, 2, 3])
        category = filters[0].selectbox("Category", ["Any"] + categories)
        state = filters[1].selectbox("State or coverage", ["Any"] + states)
        query = filters[2].text_input("Search schemes")
        visible = [
            item for item in schemes
            if (category == "Any" or item.get("category") == category)
            and (state == "Any" or item.get("state") == state)
            and query.lower() in " ".join(
                str(item.get(field) or "")
                for field in ("name", "category", "department", "state")
            ).lower()
        ]
        show_scheme_cards(visible)
    except RuntimeError as exc:
        st.error(str(exc))

elif page == "Check Eligibility":
    st.subheader("Check your potential eligibility")
    st.caption("This demo checks the rules currently stored by the backend. Confirm decisions with the official scheme authority.")
    try:
        schemes = load_schemes()
    except RuntimeError as exc:
        st.error(str(exc))
        schemes = []

    if schemes:
        scheme_names = {f"{item['name']} (ID {item['id']})": item for item in schemes}
        with st.form("eligibility_form"):
            selected_label = st.selectbox("Scheme", list(scheme_names))
            fields = st.columns(2)
            age = fields[0].number_input("Age", min_value=0, max_value=120, value=0)
            state = fields[1].selectbox("State", ["", "Telangana", "Andhra Pradesh", "Other"])
            income = fields[0].number_input("Annual family income (₹)", min_value=0, value=0, step=10000)
            occupation = fields[1].selectbox("Occupation", ["", "student", "farmer", "employed", "senior citizen", "other"])
            enrollment = fields[0].selectbox("Enrollment", ["", "college", "school", "other"])
            land_holdings = fields[1].number_input("Land holdings (acres)", min_value=0.0, value=0.0, step=0.5)
            submitted = st.form_submit_button("Check eligibility", type="primary")

        if submitted:
            user_data = {}
            if age:
                user_data["age"] = age
            if state:
                user_data["state"] = state
            if income:
                user_data["income"] = income
            if occupation:
                user_data["occupation"] = occupation
            if enrollment:
                user_data["enrollment"] = enrollment
            if land_holdings:
                user_data["land_holdings"] = land_holdings

            try:
                result = api_request(
                    "POST",
                    "/api/eligibility/check",
                    json={
                        "scheme_id": scheme_names[selected_label]["id"],
                        "user_data": user_data,
                    },
                )
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                status = result.get("status", "needs_more_info")
                if status == "eligible":
                    st.success("You appear to meet the configured criteria. Verify with the official scheme authority.")
                elif result.get("missing_fields") and not result.get("matched_fields"):
                    st.info("More information is needed before eligibility can be assessed.")
                elif status == "needs_more_info":
                    st.info("Some configured criteria match. More information is needed.")
                else:
                    st.warning("The submitted details do not match the configured criteria.")
                if result.get("matched_fields"):
                    st.write("**Matched criteria:** " + ", ".join(result["matched_fields"]))
                if result.get("missing_fields"):
                    st.write("**Missing or unmatched details:** " + ", ".join(result["missing_fields"]))

elif page == "Analyze Document":
    st.subheader("Analyze a government document")
    st.write("Upload a text-based PDF or clear image, up to 10 MB.")
    uploaded_file = st.file_uploader(
        "Choose a PDF or image",
        type=["pdf", "png", "jpg", "jpeg", "webp"],
    )
    if uploaded_file and st.button("Analyze document", type="primary"):
        contents = uploaded_file.getvalue()
        if len(contents) > 10 * 1024 * 1024:
            st.error("Files must be 10 MB or smaller.")
        else:
            mime_type = uploaded_file.type or mimetypes.guess_type(uploaded_file.name)[0] or "application/octet-stream"
            try:
                with st.spinner("Reading the document..."):
                    result = api_request(
                        "POST",
                        "/api/documents/analyze",
                        files={"file": (uploaded_file.name, contents, mime_type)},
                        timeout=120,
                    )
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                st.markdown("#### Summary")
                st.write(result.get("summary", "No summary was returned."))
                if result.get("text"):
                    with st.expander("View extracted text"):
                        st.text(result["text"])

st.divider()
st.caption("JanSahay AI provides guidance only. Verify scheme details with official government sources before applying.")
