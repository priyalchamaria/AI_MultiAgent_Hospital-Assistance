from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from agents.orchestrator_agent import OrchestratorAgent
from database.db_utils import execute_read_query
from services.logger import QueryLogger
from src.config import DB_PATH, POLICY_DIR, QUERY_LOG_PATH, RAW_CSV_PATH


FEEDBACK_PATH = Path("logs/feedback.json")

ROLE_COLUMN_ACCESS = {
    "Doctor": {
        "patient_id",
        "name",
        "age",
        "gender",
        "medical_condition",
        "admission_date",
        "doctor",
        "hospital",
        "medication",
        "test_results",
    },
    "Nurse": {
        "patient_id",
        "name",
        "age",
        "gender",
        "medical_condition",
        "admission_date",
        "hospital",
        "room_number",
        "medication",
        "test_results",
    },
    "Billing Staff": {
        "patient_id",
        "name",
        "age",
        "gender",
        "admission_date",
        "hospital",
        "insurance_provider",
        "billing_amount",
        "admission_type",
        "discharge_date",
    },
    "Administrator": {
        "patient_id",
        "name",
        "age",
        "gender",
        "blood_type",
        "medical_condition",
        "admission_date",
        "doctor",
        "hospital",
        "insurance_provider",
        "billing_amount",
        "room_number",
        "admission_type",
        "discharge_date",
        "medication",
        "test_results",
        "length_of_stay",
        "record_count",
        "average_billing_amount",
        "total_billing_amount",
        "average_age",
        "average_length_of_stay",
    },
}


def inject_styles() -> None:
    st.markdown(
        """
<style>
    .stApp {
        background: #f6f8fb;
        color: #172033;
    }
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1180px;
    }
    h1, h2, h3 {
        color: #172033;
        letter-spacing: 0;
    }
    [data-testid="stTabs"] [role="tablist"] {
        gap: 6px;
        border-bottom: 1px solid #d9e1ec;
    }
    [data-testid="stTabs"] [role="tab"] {
        background: #ffffff;
        border: 1px solid #d9e1ec;
        border-bottom: 0;
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: #0f766e;
        color: #ffffff;
    }
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d9e1ec;
        border-radius: 8px;
        padding: 14px 16px;
    }
    [data-testid="stChatMessage"] {
        background: #ffffff;
        border: 1px solid #d9e1ec;
        border-radius: 8px;
        padding: 10px 14px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #d9e1ec;
        border-radius: 8px;
    }
    .hero {
        background: linear-gradient(135deg, #0f766e 0%, #155e75 100%);
        color: white;
        padding: 26px 30px;
        border-radius: 8px;
        margin-bottom: 18px;
    }
    .hero h1 {
        color: white;
        margin: 0 0 8px 0;
        font-size: 2.05rem;
    }
    .hero p {
        margin: 0;
        max-width: 780px;
        color: #e6fffb;
        line-height: 1.55;
    }
    .section-card {
        background: #ffffff;
        border: 1px solid #d9e1ec;
        border-radius: 8px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    .section-card h3 {
        margin-top: 0;
        margin-bottom: 8px;
        font-size: 1.05rem;
    }
    .muted {
        color: #5d6b82;
        line-height: 1.55;
    }
    .pill {
        display: inline-block;
        background: #e6fffb;
        color: #0f766e;
        border: 1px solid #99f6e4;
        border-radius: 999px;
        padding: 4px 10px;
        font-size: 0.82rem;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .source-line {
        color: #5d6b82;
        font-size: 0.9rem;
        border-left: 3px solid #0f766e;
        padding-left: 10px;
        margin-top: 10px;
    }
    .turn-card {
        background: #ffffff;
        border: 1px solid #d9e1ec;
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    .question-block {
        background: #ecfeff;
        border: 1px solid #a5f3fc;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }
    .question-label {
        color: #0e7490;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .question-text {
        color: #123044;
        font-weight: 600;
    }
    .answer-label {
        color: #0f766e;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .rbac-note {
        background: #f8fafc;
        border: 1px dashed #cbd5e1;
        border-radius: 8px;
        padding: 8px 10px;
        color: #475569;
        font-size: 0.84rem;
        margin-bottom: 12px;
    }
    .control-card {
        background: #ffffff;
        border: 1px solid #d9e1ec;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 16px;
    }
    .compact-caption {
        color: #64748b;
        font-size: 0.82rem;
        margin-top: -4px;
        margin-bottom: 8px;
    }
    .feedback-row {
        border-top: 1px solid #e2e8f0;
        margin-top: 12px;
        padding-top: 10px;
    }
    .flow {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 10px;
        align-items: stretch;
        margin-top: 10px;
    }
    .flow-step {
        background: #f8fafc;
        border: 1px solid #d9e1ec;
        border-radius: 8px;
        padding: 14px;
        min-height: 96px;
    }
    .flow-step strong {
        display: block;
        color: #0f766e;
        margin-bottom: 6px;
    }
    .flow-step span {
        color: #5d6b82;
        font-size: 0.88rem;
    }
    @media (max-width: 900px) {
        .flow {
            grid-template-columns: 1fr;
        }
    }
</style>
""",
        unsafe_allow_html=True,
    )


@st.cache_resource
def load_orchestrator() -> OrchestratorAgent:
    return OrchestratorAgent()


def ensure_ready() -> bool:
    ready = DB_PATH.exists() and RAW_CSV_PATH.exists() and POLICY_DIR.exists()
    if ready:
        return True
    st.error("Project data is not prepared yet.")
    st.code(
        'python scripts\\prepare_data.py --archive "C:\\Users\\Priyal\\Downloads_new\\archive (1).zip"',
        language="powershell",
    )
    return False


def active_role() -> str:
    return st.session_state.get("active_role", "Doctor")


def filter_table_for_role(rows: list[dict], role: str) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    allowed = ROLE_COLUMN_ACCESS.get(role, ROLE_COLUMN_ACCESS["Doctor"])
    visible = [column for column in df.columns if column in allowed]
    return df[visible] if visible else df


def save_feedback(turn: dict, rating: str) -> None:
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if FEEDBACK_PATH.exists():
        try:
            feedback = json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            feedback = []
    else:
        feedback = []
    feedback.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": turn["query"],
            "selected_agent": turn["response"].get("selected_agent"),
            "rating": rating,
            "status": turn["response"].get("status"),
        }
    )
    FEEDBACK_PATH.write_text(json.dumps(feedback[-500:], indent=2), encoding="utf-8")


def render_response(response: dict) -> None:
    status = response.get("status", "success")
    if status in {"blocked", "unsupported", "not_found"}:
        st.warning(response["answer"])
    else:
        st.markdown(response["answer"])

    if response.get("sql_query"):
        st.markdown("**Generated SQL**")
        st.code(response["sql_query"], language="sql")
    if response.get("table"):
        role = active_role()
        df = filter_table_for_role(response["table"], role)
        if not df.empty:
            if len(df.columns) != len(pd.DataFrame(response["table"]).columns):
                st.markdown(
                    f"<div class='rbac-note'>Showing fields permitted for <strong>{html.escape(role)}</strong>.</div>",
                    unsafe_allow_html=True,
                )
            st.dataframe(df, use_container_width=True, hide_index=True)
    if response.get("sources"):
        best_source = response["sources"][0]
        source_name = str(best_source.get("source", "")).replace("_", " ").replace(".txt", "").title()
        st.markdown(
            f"<div class='source-line'>Source: {source_name}, {best_source.get('section')}</div>",
            unsafe_allow_html=True,
        )
        with st.expander("Why this answer?", expanded=False):
            st.caption(
                f"{response.get('selected_agent', '-')} | confidence {response.get('confidence', 0)} | "
                f"{response.get('response_time', 0)}s | {status}"
            )
            st.write(response.get("route_reason", "No explanation available."))
            for source in response["sources"][:2]:
                st.markdown(f"**{source.get('source')}** - {source.get('section')} - score `{source.get('score')}`")


def render_feedback(turn: dict) -> None:
    labels = ["Helpful", "Not helpful", "Incorrect"]
    with st.expander("Feedback", expanded=False):
        st.caption("Was this answer useful?")
        cols = st.columns([0.9, 1.1, 0.9, 5])
        turn_id = turn.get("id", f"turn_{abs(hash(turn.get('query', '')))}")
        for index, label in enumerate(labels):
            if cols[index].button(label, key=f"feedback_{turn_id}_{label}", use_container_width=True):
                turn["feedback"] = label
                save_feedback(turn, label)
                st.toast(f"Feedback saved: {label}")
        if turn.get("feedback"):
            st.caption(f"Feedback recorded: {turn['feedback']}")


def render_turn(turn: dict) -> None:
    st.markdown("<div class='turn-card'>", unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="question-block">
    <div class="question-label">Your Question</div>
    <div class="question-text">{html.escape(turn["query"])}</div>
</div>
<div class="answer-label">Answer</div>
""",
        unsafe_allow_html=True,
    )
    render_response(turn["response"])
    render_feedback(turn)
    st.markdown("</div>", unsafe_allow_html=True)


def chat_tab() -> None:
    orchestrator = load_orchestrator()
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "chat_turns" not in st.session_state:
        st.session_state.chat_turns = []

    examples = [
        "How many female patients have diabetes?",
        "How many patients have diabetes?",
        "How many emergency admissions were there?",
        "How many abnormal test results were recorded?",
        "What is the average billing amount by insurance provider?",
        "What is the average length of stay by admission type?",
        "Show the top 5 hospitals with the most cancer patients.",
        "List patients with abnormal test results.",
        "What is the visitor policy?",
        "What are the visiting hours?",
        "What is the discharge policy?",
        "What is the patient privacy policy?",
        "When should privacy incidents be reported?",
        "What is the medication administration policy?",
        "When should medication discrepancies be escalated?",
        "What is the infection control policy?",
        "What is the billing and insurance policy?",
        "How many diabetic patients are there and what is the discharge policy?",
        "What is the weather today?",
    ]
    st.markdown(
        """
<div class="section-card">
    <h3>Ask CareBridge AI</h3>
    <div class="muted">Use plain English to query patient records, hospital policy documents, or both in one question.</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='control-card'>", unsafe_allow_html=True)
    role_col, question_col, button_col = st.columns([1, 3.2, 0.8], vertical_alignment="bottom")
    with role_col:
        st.session_state.active_role = st.selectbox(
            "Access role",
            ["Doctor", "Nurse", "Billing Staff", "Administrator"],
            index=["Doctor", "Nurse", "Billing Staff", "Administrator"].index(active_role()),
            help="Demo access control: patient-table columns are filtered based on the selected hospital staff role.",
        )
    with question_col:
        selected = st.selectbox("Choose a question", examples)
    with button_col:
        ask_clicked = st.button("Ask", use_container_width=True)
    typed_query = st.text_input(
        "Or type your own question",
        key="typed_query",
        placeholder="Type a custom question here...",
    )
    st.markdown(
        "<div class='compact-caption'>Access role only controls which patient-table fields are visible in the UI. It does not change policy answers.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    prompt = None
    if st.session_state.get("pending_query"):
        prompt = st.session_state.pop("pending_query")
    elif ask_clicked:
        prompt = typed_query.strip() if typed_query.strip() else selected

    if prompt:
        response = orchestrator.process_query(prompt, st.session_state.conversation_history)
        st.session_state.conversation_history.append(response)
        st.session_state.conversation_history = st.session_state.conversation_history[-6:]
        st.session_state.chat_turns.append(
            {
                "id": f"turn_{len(st.session_state.chat_turns) + 1}",
                "query": prompt,
                "response": response,
                "role": active_role(),
            }
        )
        st.rerun()

    if st.session_state.chat_turns:
        st.markdown("#### Recent Questions")
    for turn in reversed(st.session_state.chat_turns):
        render_turn(turn)


def database_tab() -> None:
    st.subheader("Database Explorer")
    role = st.selectbox(
        "View as staff role",
        ["Doctor", "Nurse", "Billing Staff", "Administrator"],
        index=["Doctor", "Nurse", "Billing Staff", "Administrator"].index(active_role()),
        key="database_role",
    )
    st.session_state.active_role = role
    counts = execute_read_query("SELECT COUNT(*) AS total_records FROM patients")
    condition_count = execute_read_query("SELECT COUNT(DISTINCT medical_condition) AS total FROM patients")
    hospital_count = execute_read_query("SELECT COUNT(DISTINCT hospital) AS total FROM patients")
    cols = st.columns(3)
    cols[0].metric("Patient records", f"{int(counts.iloc[0, 0]):,}")
    cols[1].metric("Medical conditions", int(condition_count.iloc[0, 0]))
    cols[2].metric("Hospitals", f"{int(hospital_count.iloc[0, 0]):,}")
    st.divider()
    cols = st.columns(3)
    cols[0].dataframe(
        execute_read_query("SELECT medical_condition, COUNT(*) AS count FROM patients GROUP BY medical_condition ORDER BY count DESC"),
        use_container_width=True,
        hide_index=True,
    )
    cols[1].dataframe(
        execute_read_query("SELECT admission_type, COUNT(*) AS count FROM patients GROUP BY admission_type ORDER BY count DESC"),
        use_container_width=True,
        hide_index=True,
    )
    cols[2].dataframe(
        execute_read_query("SELECT test_results, COUNT(*) AS count FROM patients GROUP BY test_results ORDER BY count DESC"),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("#### Sample Records")
    sample = execute_read_query(
        "SELECT patient_id, name, age, gender, blood_type, medical_condition, admission_date, doctor, hospital, "
        "insurance_provider, billing_amount, room_number, admission_type, discharge_date, medication, test_results "
        "FROM patients LIMIT 25"
    )
    st.markdown(
        f"<div class='rbac-note'>Role-based access control demo: <strong>{html.escape(role)}</strong> view.</div>",
        unsafe_allow_html=True,
    )
    st.dataframe(filter_table_for_role(sample.to_dict("records"), role), use_container_width=True, hide_index=True)


def policies_tab() -> None:
    st.subheader("Policy Library")
    policy_files = sorted(POLICY_DIR.glob("*.txt"))
    selected = st.selectbox("Select policy", [path.name for path in policy_files])
    path = POLICY_DIR / selected
    content = path.read_text(encoding="utf-8")
    metadata = extract_policy_metadata(content)

    cols = st.columns(4)
    cols[0].metric("Policy documents", len(policy_files))
    cols[1].metric("Policy ID", metadata.get("Policy ID", "N/A"))
    cols[2].metric("Sections", count_policy_sections(content))
    cols[3].metric("Words", len(content.split()))

    st.markdown(
        """
<div class="section-card">
    <h3>RAG Source Library</h3>
    <div class="muted">
        These synthetic policies are the source documents used by the RAG Agent.
        CareBridge AI retrieves relevant sections from this library and cites the policy section used in each answer.
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    detail_cols = st.columns(2)
    detail_cols[0].info(f"Title: {metadata.get('Policy Title', selected)}")
    detail_cols[1].info(f"Review Date: {metadata.get('Review Date', 'N/A')}")
    st.text_area("Selected Policy Text", content, height=520)


def extract_policy_metadata(content: str) -> dict[str, str]:
    metadata = {}
    for key in ["Policy Title", "Policy ID", "Review Date"]:
        match = re.search(rf"^{key}:\s*(.+)$", content, flags=re.MULTILINE)
        if match:
            metadata[key] = match.group(1).strip()
    return metadata


def count_policy_sections(content: str) -> int:
    return len(
        re.findall(
            r"^(Purpose|Scope|Responsibilities|Procedure|Exceptions|Escalation Process|Review Date):",
            content,
            flags=re.MULTILINE,
        )
    )


def metrics_tab() -> None:
    st.subheader("Query Activity")
    logs = QueryLogger(QUERY_LOG_PATH).read_logs()
    if not logs:
        st.info("No queries have been logged yet.")
        return
    df = pd.DataFrame(logs)
    cols = st.columns(4)
    cols[0].metric("Logged queries", len(df))
    cols[1].metric("Average response time", round(df["response_time"].mean(), 3))
    cols[2].metric("Success rate", f"{round((df['status'] == 'success').mean() * 100, 1)}%")
    cols[3].metric("Most used route", df["route"].mode().iloc[0])
    st.bar_chart(df["route"].value_counts())
    st.dataframe(df.tail(50).sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)


def evaluation_tab() -> None:
    st.subheader("Validation Results")
    path = Path("evaluation/results.json")
    if path.exists():
        results = json.loads(path.read_text(encoding="utf-8"))
        cols = st.columns(4)
        cols[0].metric("Routing accuracy", f"{results.get('routing_accuracy', 0) * 100:.1f}%")
        cols[1].metric("Success rate", f"{results.get('end_to_end_success_rate', 0) * 100:.1f}%")
        cols[2].metric("Avg latency", f"{results.get('average_latency', 0)}s")
        cols[3].metric("Unsafe blocked", results.get("unsafe_query_blocking_rate", 0))
        rows = pd.DataFrame(results.get("confusion_rows", []))
        if not rows.empty:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        with st.expander("Raw validation output", expanded=False):
            st.json(results)
    else:
        st.info("Run `python evaluation\\evaluate_system.py` to generate evaluation metrics.")
    st.caption("Validation checks routing accuracy, unsafe-query blocking, SQL execution, latency, and policy citation retrieval.")


def about_tab() -> None:
    st.subheader("Project Overview")
    st.markdown(
        """
<div class="section-card">
    <h3>CareBridge AI Multi-Agent Hospital Assistant</h3>
    <div class="muted">
        CareBridge AI provides one conversational entry point for structured patient-record analysis and
        unstructured hospital-policy retrieval. It is built as an academic final project using synthetic
        healthcare data and synthetic policy documents.
    </div>
</div>
<div class="section-card">
    <h3>Architecture</h3>
    <div class="flow">
        <div class="flow-step"><strong>1. User Query</strong><span>Hospital staff ask in plain English.</span></div>
        <div class="flow-step"><strong>2. Orchestrator</strong><span>Classifies SQL, RAG, both, or unsupported.</span></div>
        <div class="flow-step"><strong>3. Specialist Agents</strong><span>SQL Agent queries SQLite; RAG Agent searches policies.</span></div>
        <div class="flow-step"><strong>4. Safety Layer</strong><span>Blocks unsafe SQL and applies role-based display permissions.</span></div>
        <div class="flow-step"><strong>5. Response</strong><span>Returns answer, evidence, logs, and feedback signal.</span></div>
    </div>
</div>
<div class="section-card">
    <h3>Project Strengths</h3>
    <span class="pill">Multi-agent routing</span>
    <span class="pill">SQLite patient database</span>
    <span class="pill">RAG with citations</span>
    <span class="pill">SQL safety layer</span>
    <span class="pill">Role-based access demo</span>
    <span class="pill">Answer feedback</span>
    <span class="pill">Conversation memory</span>
    <span class="pill">Automated tests</span>
    <span class="pill">Evaluation metrics</span>
</div>
<div class="section-card">
    <h3>Academic Use Notice</h3>
    <div class="muted">
        The data and policies are synthetic. This application is not intended for real clinical decisions,
        diagnosis, treatment planning, or production hospital use.
    </div>
</div>
"""
,
        unsafe_allow_html=True,
    )


def render_app() -> None:
    st.set_page_config(page_title="CareBridge AI", page_icon="C", layout="wide")
    inject_styles()
    st.markdown(
        """
<div class="hero">
    <h1>CareBridge AI Multi-Agent Hospital Assistant</h1>
    <p>Plain-English access to synthetic patient records and hospital policy documents through a routed SQL and RAG workflow.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    if not ensure_ready():
        return

    tabs = st.tabs(["Chat", "Database", "Policies", "Activity", "Validation", "About"])
    with tabs[0]:
        chat_tab()
    with tabs[1]:
        database_tab()
    with tabs[2]:
        policies_tab()
    with tabs[3]:
        metrics_tab()
    with tabs[4]:
        evaluation_tab()
    with tabs[5]:
        about_tab()
