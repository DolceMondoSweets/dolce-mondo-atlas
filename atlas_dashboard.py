import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Atlas — Dolce Mondo", layout="wide")
st.title("Atlas")
st.markdown("**Dolce Mondo AI Operating System**")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Morning Brief", "Chat with Atlas", "10 Questions", "Decisions Log", "Data Upload"])

if page == "Morning Brief":
    st.header("Good Morning, Founder")
    st.write(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
    
    st.success("**Overall Business Health:** Not yet fully scoreable — major data gaps (cash, COGS, current sales)")
    st.info("**Business Momentum:** Neutral — physical paused, e-comm limited success")
    st.warning("**Cash Runway:** Unknown — need current cash position & burn rate")
    
    st.subheader("Today's Biggest Opportunity")
    st.write("Push Experiential Kit + complete trailer improvements for reopening.")
    
    st.subheader("Biggest Risk")
    st.write("DSHS inspection not yet scheduled — lease expires Sep 1.")
    
    st.subheader("Recommended Focus Today")
    st.write("1. Get cash balance + Square export\n2. Follow up on DSHS inspection\n3. Log any decisions")
    
    st.subheader("Today's Top 5 Priorities")
    st.write("1. Get Bank of America cash balance\n2. Export Square sales data\n3. Confirm DSHS inspection timeline\n4. Push Experiential Kit content\n5. Log this week's decisions")

elif page == "Chat with Atlas":
    st.header("Chat with Atlas")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    if prompt := st.chat_input("Ask Atlas anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            response = "I'm Atlas. To make this real, we need to connect to Claude API or copy-paste responses for now. For the MVP, paste Claude's reply here."
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

elif page == "10 Questions":
    st.header("The 10 Questions")
    questions = [
        "1. Am I making money?",
        "2. Am I running out of money?",
        "3. Are sales growing?",
        "4. Are customers happy?",
        "5. Are operations healthy?",
        "6. Is my team performing?",
        "7. Are we executing our goals?",
        "8. What risks are coming?",
        "9. What opportunities am I missing?",
        "10. What should I do today?"
    ]
    for q in questions:
        st.write(f"**{q}**")
        st.write("*(Answer updates when data is provided)*")
        st.divider()

elif page == "Decisions Log":
    st.header("Executive Memory — Decisions Log")
    st.write("This is where Atlas remembers every important decision and its outcome.")
    st.text_area("Log a new decision here (then copy to 08_Decisions_Log.md)", height=150)

elif page == "Data Upload":
    st.header("Upload Data for Finance")
    st.write("Upload Square CSV or Bank export here (future version will auto-process)")
    uploaded_file = st.file_uploader("Upload file", type=["csv", "xlsx"])
    if uploaded_file:
        st.success("File received — Finance Module will use this in next brief.")

st.caption("Atlas v0.1 — Powered by your knowledge base + Claude")