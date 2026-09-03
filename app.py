import streamlit as st
import json
import os
import sys
import requests
from datetime import datetime

st.set_page_config(
    page_title="Lakshita's Job Agent",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Serif+Display:ital@0;1&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #FAFAF8;
}

section[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #EBEBEB;
}

section[data-testid="stSidebar"] > div {
    padding: 2rem 1.5rem;
}

.sidebar-title {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: #1A1A1A;
    margin-bottom: 0.25rem;
}

.sidebar-sub {
    font-size: 12px;
    color: #999;
    margin-bottom: 2rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.app-card {
    background: #FFFFFF;
    border: 1px solid #EBEBEB;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.15s;
}

.app-card:hover {
    border-color: #C8C8C8;
}

.app-company {
    font-size: 14px;
    font-weight: 500;
    color: #1A1A1A;
    margin: 0;
}

.app-role {
    font-size: 12px;
    color: #888;
    margin: 2px 0 8px;
}

.status-pill {
    display: inline-block;
    font-size: 11px;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.02em;
}

.status-applied { background: #EAF3DE; color: #3B6D11; }
.status-interviewing { background: #E6F1FB; color: #185FA5; }
.status-offer { background: #E1F5EE; color: #0F6E56; }
.status-rejected { background: #FCEBEB; color: #A32D2D; }
.status-default { background: #F1EFE8; color: #5F5E5A; }

.chat-container {
    max-width: 720px;
    margin: 0 auto;
    padding: 2rem 1rem 6rem;
}

.chat-header {
    text-align: center;
    padding: 3rem 0 2rem;
}

.chat-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 36px;
    color: #1A1A1A;
    font-weight: 400;
    margin: 0;
}

.chat-header p {
    font-size: 14px;
    color: #999;
    margin: 0.5rem 0 0;
}

.user-bubble {
    background: #1A1A1A;
    color: #FFFFFF;
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1.1rem;
    max-width: 80%;
    margin-left: auto;
    margin-bottom: 1.25rem;
    font-size: 14px;
    line-height: 1.6;
}

.agent-bubble {
    background: #FFFFFF;
    border: 1px solid #EBEBEB;
    border-radius: 4px 18px 18px 18px;
    padding: 1rem 1.25rem;
    max-width: 88%;
    margin-bottom: 1.25rem;
    font-size: 14px;
    line-height: 1.7;
    color: #2A2A2A;
}

.agent-bubble h2, .agent-bubble h3 {
    font-size: 15px;
    font-weight: 500;
    margin: 1rem 0 0.4rem;
    color: #1A1A1A;
}

.agent-bubble strong {
    font-weight: 500;
    color: #1A1A1A;
}

.thinking-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #F4F4F0;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    color: #888;
    margin-bottom: 1.25rem;
}

.section-label {
    font-size: 11px;
    font-weight: 500;
    color: #AAAAAA;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 1.5rem 0 0.75rem;
}

.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #BBBBBB;
    font-size: 13px;
}

.empty-icon {
    font-size: 28px;
    margin-bottom: 0.5rem;
}

div[data-testid="stChatInput"] {
    background: transparent;
}

div[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 1px solid #DDDDD8 !important;
    border-radius: 24px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important;
}

.stButton > button {
    background: transparent;
    border: 1px solid #DDDDD8;
    border-radius: 8px;
    color: #666;
    font-size: 12px;
    font-family: 'DM Sans', sans-serif;
    padding: 0.35rem 0.85rem;
    transition: all 0.15s;
}

.stButton > button:hover {
    border-color: #999;
    color: #333;
    background: #F7F7F5;
}

.clear-btn > button {
    color: #CC4444;
    border-color: #FFCECE;
}

.clear-btn > button:hover {
    background: #FFF0F0;
    border-color: #CC4444;
}
</style>
""", unsafe_allow_html=True)


def get_status_class(status):
    if not status:
        return "status-default"
    s = status.lower()
    if "interview" in s:
        return "status-interviewing"
    elif "offer" in s:
        return "status-offer"
    elif "reject" in s:
        return "status-rejected"
    elif "applied" in s or "not started" in s:
        return "status-applied"
    return "status-default"


def load_notion_applications():
    try:
        notion_key = os.getenv("NOTION_API_KEY")
        db_id = os.getenv("NOTION_DATABASE_ID")
        if not notion_key or not db_id:
            return []
        resp = requests.post(
            f"https://api.notion.com/v1/databases/{db_id}/query",
            headers={
                "Authorization": f"Bearer {notion_key}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            },
            json={"page_size": 20}
        )
        if resp.status_code != 200:
            return []
        results = resp.json().get("results", [])
        apps = []
        for r in results:
            props = r.get("properties", {})
            company = ""
            if "Company" in props and props["Company"].get("title"):
                company = props["Company"]["title"][0]["plain_text"] if props["Company"]["title"] else ""
            role = ""
            if "Role" in props and props["Role"].get("rich_text"):
                role = props["Role"]["rich_text"][0]["plain_text"] if props["Role"]["rich_text"] else ""
            status = ""
            if "Status" in props and props["Status"].get("status"):
                status = props["Status"]["status"]["name"]
            if company:
                apps.append({"company": company, "role": role, "status": status})
        return apps
    except Exception:
        return []


def load_messages_from_file():
    try:
        path = os.path.join(os.path.dirname(__file__), "state", "messages.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read()
                if content:
                    return json.loads(content)
    except Exception:
        pass
    return []


def run_agent_query(user_message):
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from dotenv import load_dotenv
        load_dotenv()
        from agent.core.loop import run_agent
        return run_agent(user_message)
    except Exception as e:
        return f"Error running agent: {str(e)}"


# ─── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-title">✦ Job Agent</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-sub">Lakshita Vij · NYU CS</p>', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Applications</p>', unsafe_allow_html=True)

    apps = load_notion_applications()
    if apps:
        for app in apps:
            status_class = get_status_class(app["status"])
            st.markdown(f"""
            <div class="app-card">
                <p class="app-company">{app['company']}</p>
                <p class="app-role">{app['role'] or 'Role not specified'}</p>
                <span class="status-pill {status_class}">{app['status'] or 'Tracking'}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">○</div>
            No applications yet.<br>Ask the agent to track one.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<p class="section-label">Quick prompts</p>', unsafe_allow_html=True)

    quick_prompts = [
        "Find me neurotech jobs in NYC",
        "Evaluate my resume fit",
        "Draft a cold email",
        "What should I work on next?",
    ]
    for qp in quick_prompts:
        if st.button(qp, key=f"qp_{qp}"):
            st.session_state.quick_prompt = qp

    st.markdown("---")
    with st.container():
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("Clear conversation", key="clear"):
            st.session_state.messages = []
            try:
                path = os.path.join(os.path.dirname(__file__), "state", "messages.json")
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─── Main chat ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_prompt" in st.session_state:
    quick = st.session_state.pop("quick_prompt")
    st.session_state.pending_prompt = quick

col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-header">
            <h1>Good morning, Lakshita.</h1>
            <p>What are you working on today?</p>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="agent-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

    prompt = st.chat_input("Ask the agent anything...")

    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pop("pending_prompt")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)

        with st.spinner(""):
            st.markdown('<div class="thinking-pill">✦ thinking</div>', unsafe_allow_html=True)
            response = run_agent_query(prompt)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown(f'<div class="agent-bubble">{response}</div>', unsafe_allow_html=True)
        st.rerun()