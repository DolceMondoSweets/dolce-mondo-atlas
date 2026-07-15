"""
Atlas — Dolce Mondo AI Operating System
Production-ready Streamlit dashboard.

Run locally:   streamlit run atlas_app.py
Deploy:        push this folder (incl. knowledge_base/) to your Streamlit Cloud repo.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
import pandas as pd
import anthropic

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

APP_TITLE = "Atlas"
APP_SUBTITLE = "Dolce Mondo AI Operating System"
MODEL = "claude-sonnet-5"
DATA_FILE = Path(__file__).parent / "atlas_data.json"
KB_DIR = Path(__file__).parent / "knowledge_base"

TEN_QUESTIONS = [
    "What is my cash position and how many days of runway do I have?",
    "What changed in revenue or sales since yesterday/last week?",
    "What is the single highest-leverage task I should do today?",
    "What decisions are waiting on me, and what happens if I delay them?",
    "What risk (permitting, cash, ops, reputation) is most urgent right now?",
    "What did the customer/market tell me recently that I haven't acted on?",
    "What is the status of the H-E-B micro-café reopening?",
    "What is the status of fundraising / investor conversations?",
    "What marketing or ecommerce action would move the needle this week?",
    "What should I NOT spend time on today?",
]

# ─────────────────────────────────────────────────────────────
# PERSISTENCE
# Note: On Streamlit Community Cloud, local disk is wiped on redeploy/reboot,
# so this JSON file is durable *between reruns and most restarts* but not
# guaranteed forever. For real durability, swap this for Google Sheets,
# Supabase, or a small hosted database — same load_data()/save_data()
# interface, different backend.
# ─────────────────────────────────────────────────────────────

DEFAULT_DATA = {
    "cash": 8709.65,
    "burn": 5000.0,
    "runway": 52,
    "revenue_mtd": 0.0,
    "decisions": [],  # list of {date, text}
}


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            # backfill any missing keys from defaults
            for k, v in DEFAULT_DATA.items():
                data.setdefault(k, v)
            return data
        except (json.JSONDecodeError, OSError):
            st.warning("Data file was unreadable — starting fresh.")
    return DEFAULT_DATA.copy()


def save_data(data: dict) -> None:
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        st.error(f"Could not save data: {e}")


# ─────────────────────────────────────────────────────────────
# KNOWLEDGE BASE
# Drop your 11 .md files into the knowledge_base/ folder next to this file.
# ─────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_knowledge_base() -> dict:
    """Returns {filename: content} for every .md file in knowledge_base/."""
    kb = {}
    if KB_DIR.exists():
        for path in sorted(KB_DIR.glob("*.md")):
            try:
                kb[path.name] = path.read_text(encoding="utf-8")
            except OSError:
                continue
    return kb


def kb_context(selected_files: list[str] | None = None, char_limit: int = 40000) -> str:
    """Concatenate selected (or all) KB files into a single context string,
    trimmed to a rough character budget so prompts don't blow up."""
    kb = load_knowledge_base()
    files = selected_files if selected_files else list(kb.keys())
    chunks = []
    total = 0
    for name in files:
        content = kb.get(name, "")
        if total + len(content) > char_limit:
            content = content[: max(0, char_limit - total)]
        chunks.append(f"### {name}\n{content}")
        total += len(content)
        if total >= char_limit:
            break
    return "\n\n".join(chunks)


# ─────────────────────────────────────────────────────────────
# CLAUDE API
# ─────────────────────────────────────────────────────────────

def get_client() -> anthropic.Anthropic | None:
    api_key = st.session_state.get("api_key", "")
    if api_key and api_key.startswith("sk-ant-"):
        return anthropic.Anthropic(api_key=api_key)
    return None


def ask_claude(client: anthropic.Anthropic, system: str, user_message: str,
                max_tokens: int = 2000) -> str | None:
    """Single point of contact with the API. Handles text extraction and errors."""
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        text = next((b.text for b in message.content if b.type == "text"), None)
        if not text:
            st.error("Claude returned no text content. Try again.")
        return text
    except anthropic.APIError as e:
        st.error(f"Anthropic API error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    return None


# ─────────────────────────────────────────────────────────────
# ACCESS CONTROL
# This is a public URL, so it needs a lock on the front door before it
# holds real cash/burn/decisions data. The password lives in Streamlit
# Cloud's "Secrets" settings (a form in the dashboard, not a code file),
# so it's never committed to your repo.
# ─────────────────────────────────────────────────────────────

def check_password() -> bool:
    """Returns True once the correct password has been entered this session."""
    if st.session_state.get("authenticated", False):
        return True

    st.title(APP_TITLE)
    st.markdown(f"**{APP_SUBTITLE}**")
    st.subheader("🔒 Enter password to continue")

    configured_password = st.secrets.get("APP_PASSWORD", None)
    if not configured_password:
        st.error(
            "No password is configured yet. Add APP_PASSWORD in your Streamlit Cloud "
            "app's Settings → Secrets, e.g.:\n\nAPP_PASSWORD = \"your-password-here\""
        )
        return False

    entered = st.text_input("Password", type="password")
    if st.button("Enter"):
        if entered == configured_password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


def finance_snapshot_str(data: dict) -> str:

    return (
        f"Current Cash Balance: ${data['cash']:,.2f}\n"
        f"Monthly Burn Rate: ${data['burn']:,.2f}\n"
        f"Runway: {data['runway']} days\n"
        f"Month-to-Date Revenue: ${data['revenue_mtd']:,.2f}\n"
        f"Today's Date: {datetime.now().strftime('%B %d, %Y')}"
    )


# ─────────────────────────────────────────────────────────────
# PAGE: Morning Brief
# ─────────────────────────────────────────────────────────────

def page_morning_brief(data: dict, client):
    st.header("Good Morning, Founder")
    st.write(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")

    st.success(
        f"**Finance Snapshot** — Cash: ${data['cash']:,.2f} | "
        f"Burn: ${data['burn']:,.2f} | Runway: {data['runway']} days | "
        f"MTD Revenue: ${data['revenue_mtd']:,.2f}"
    )

    if st.button("Generate Fresh Morning Brief", type="primary"):
        if client is None:
            st.error("Enter a valid Anthropic API key in the sidebar first.")
            return
        with st.spinner("Asking Claude..."):
            system = (
                "You are Atlas, the AI operating system for Dolce Mondo, a Houston-based "
                "coffee, beverage, and sweets brand. Respond ONLY with clean plain text in "
                "a Morning Brief format: start with 'Good Morning', then short sections for "
                "Finance, Priorities, and Risks. Base finance commentary strictly on the "
                "numbers provided — never invent figures. Use the business context below "
                "for tone and priorities, but only state facts that are supported by it "
                "or by the finance snapshot."
            )
            user_msg = (
                f"BUSINESS CONTEXT:\n{kb_context()}\n\n"
                f"FINANCE SNAPSHOT:\n{finance_snapshot_str(data)}\n\n"
                "Give me this morning's brief."
            )
            brief = ask_claude(client, system, user_msg)
            if brief:
                st.markdown("### Atlas Morning Brief")
                st.markdown(brief)
    else:
        st.info("Click the button to generate a fresh brief.")


# ─────────────────────────────────────────────────────────────
# PAGE: Finance Data
# ─────────────────────────────────────────────────────────────

def page_finance_data(data: dict):
    st.header("Finance Data")
    col1, col2 = st.columns(2)
    with col1:
        cash = st.number_input("Current Cash Balance ($)", value=float(data["cash"]))
        burn = st.number_input("Monthly Burn Rate ($)", value=float(data["burn"]))
    with col2:
        runway = st.number_input("Calculated Runway (days)", value=int(data["runway"]))

    if st.button("Save Finance Data", type="primary"):
        data["cash"], data["burn"], data["runway"] = cash, burn, runway
        save_data(data)
        st.success("Saved.")


# ─────────────────────────────────────────────────────────────
# PAGE: Square Data
# ─────────────────────────────────────────────────────────────

def page_square_data(data: dict):
    st.header("Square Data")

    revenue_mtd = st.number_input("MTD Revenue ($, manual entry)", value=float(data["revenue_mtd"]))
    if st.button("Save Manual Revenue", type="primary"):
        data["revenue_mtd"] = revenue_mtd
        save_data(data)
        st.success("Saved.")

    st.divider()
    st.subheader("Or upload a Square CSV export")
    uploaded = st.file_uploader("Square sales CSV", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            st.dataframe(df.head(20), use_container_width=True)

            amount_col = next(
                (c for c in df.columns if c.strip().lower() in
                 ("net total", "total", "gross sales", "amount")),
                None,
            )
            if amount_col:
                cleaned = (
                    df[amount_col]
                    .astype(str)
                    .str.replace(r"[$,]", "", regex=True)
                    .astype(float)
                )
                total = cleaned.sum()
                st.metric("Detected total from CSV", f"${total:,.2f}")
                if st.button(f"Use ${total:,.2f} as MTD Revenue"):
                    data["revenue_mtd"] = float(total)
                    save_data(data)
                    st.success("MTD Revenue updated from CSV.")
            else:
                st.warning(
                    "Couldn't auto-detect a total column. Expected one of: "
                    "'Net Total', 'Total', 'Gross Sales', 'Amount'."
                )
        except Exception as e:
            st.error(f"Could not read CSV: {e}")


# ─────────────────────────────────────────────────────────────
# PAGE: 10 Questions
# ─────────────────────────────────────────────────────────────

def page_ten_questions(data: dict, client):
    st.header("The 10 Questions")
    st.caption("The daily check-in every founder should be able to answer.")

    with st.expander("Edit the questions", expanded=False):
        st.write("Current list:")
        for i, q in enumerate(TEN_QUESTIONS, 1):
            st.write(f"{i}. {q}")
        st.caption("To change these, edit TEN_QUESTIONS in atlas_app.py.")

    if st.button("Get Atlas's Answers", type="primary"):
        if client is None:
            st.error("Enter a valid Anthropic API key in the sidebar first.")
            return
        with st.spinner("Thinking through today..."):
            system = (
                "You are Atlas, the AI operating system for Dolce Mondo. Answer each of "
                "the 10 questions concisely (2-4 sentences each), numbered to match. "
                "Where the answer depends on facts not in your context, say so plainly "
                "instead of guessing. Use the business context and finance snapshot given."
            )
            questions_block = "\n".join(f"{i}. {q}" for i, q in enumerate(TEN_QUESTIONS, 1))
            user_msg = (
                f"BUSINESS CONTEXT:\n{kb_context()}\n\n"
                f"FINANCE SNAPSHOT:\n{finance_snapshot_str(data)}\n\n"
                f"QUESTIONS:\n{questions_block}"
            )
            answers = ask_claude(client, system, user_msg, max_tokens=2500)
            if answers:
                st.markdown(answers)


# ─────────────────────────────────────────────────────────────
# PAGE: Decisions Log
# ─────────────────────────────────────────────────────────────

def page_decisions_log(data: dict):
    st.header("Decisions Log")
    st.caption("A running record of decisions made — for you and for investors.")

    with st.form("new_decision", clear_on_submit=True):
        text = st.text_area("Log a decision", placeholder="What did you decide, and why?")
        submitted = st.form_submit_button("Save Decision")
        if submitted and text.strip():
            data["decisions"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "text": text.strip(),
            })
            save_data(data)
            st.success("Decision logged.")

    st.divider()
    if not data["decisions"]:
        st.info("No decisions logged yet.")
    else:
        for entry in reversed(data["decisions"]):
            st.markdown(f"**{entry['date']}**")
            st.write(entry["text"])
            st.markdown("---")


# ─────────────────────────────────────────────────────────────
# PAGE: Chat with Atlas
# ─────────────────────────────────────────────────────────────

def page_chat(data: dict, client):
    st.header("Chat with Atlas")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask Atlas anything about the business...")
    if prompt:
        if client is None:
            st.error("Enter a valid Anthropic API key in the sidebar first.")
            return
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                system = (
                    "You are Atlas, the AI operating system for Dolce Mondo, a Houston-based "
                    "coffee, beverage, and sweets brand run solo by its founder. Be direct "
                    "and concrete. Ground answers in the business context and finance "
                    "snapshot provided; say clearly when something isn't covered by them."
                )
                user_msg = (
                    f"BUSINESS CONTEXT:\n{kb_context()}\n\n"
                    f"FINANCE SNAPSHOT:\n{finance_snapshot_str(data)}\n\n"
                    f"QUESTION:\n{prompt}"
                )
                reply = ask_claude(client, system, user_msg)
                if reply:
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title=f"{APP_TITLE} — Dolce Mondo", layout="centered")

    if not check_password():
        return

    if "data" not in st.session_state:
        st.session_state.data = load_data()
    data = st.session_state.data

    st.title(APP_TITLE)
    st.markdown(f"**{APP_SUBTITLE}**")

    with st.sidebar:
        if st.button("🔒 Lock Atlas"):
            st.session_state.authenticated = False
            st.rerun()

        st.header("Atlas Status")
        api_key = st.text_input("Anthropic API Key (sk-ant-...)", type="password",
                                 value=st.session_state.get("api_key", ""))
        st.session_state.api_key = api_key
        client = get_client()
        st.write("🔑 API key:", "✅ connected" if client else "❌ not set")

        kb = load_knowledge_base()
        st.write("📚 Knowledge base:", f"✅ {len(kb)} files" if kb else "❌ none found")
        if not kb:
            st.caption(f"Drop your .md files into: `{KB_DIR}`")

        st.write("💾 Data file:", "✅ found" if DATA_FILE.exists() else "ℹ️ will be created on first save")

        st.divider()
        st.header("Navigation")
        page = st.radio(
            "Go to",
            ["Morning Brief", "Finance Data", "Square Data", "10 Questions",
             "Decisions Log", "Chat with Atlas"],
            label_visibility="collapsed",
        )

    if page == "Morning Brief":
        page_morning_brief(data, client)
    elif page == "Finance Data":
        page_finance_data(data)
    elif page == "Square Data":
        page_square_data(data)
    elif page == "10 Questions":
        page_ten_questions(data, client)
    elif page == "Decisions Log":
        page_decisions_log(data)
    elif page == "Chat with Atlas":
        page_chat(data, client)

    st.caption("Atlas — production MVP")


if __name__ == "__main__":
    main()
