import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import time

# Page Config
st.set_page_config(
    page_title="FinSolve Chatbot 💬",
    page_icon="🤖",
    layout="centered"
)

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "history" not in st.session_state:
    st.session_state.history = []   # list of (question, answer)

# Sidebar: Authentication
with st.sidebar:
    st.header("🔐 User Login")

    if not st.session_state.user:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            try:
                res = requests.get(
                    "http://127.0.0.1:8000/login",
                    auth=HTTPBasicAuth(u, p)
                )
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.user = {"username": u, "role": data["role"]}
                    st.success(f"Welcome {u}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            except Exception as err:
                st.error(f"🚫 Backend unreachable: {err}")
    else:
        st.markdown(f"**👤 User:** `{st.session_state.user['username']}`")
        st.markdown(f"**🧾 Role:** `{st.session_state.user['role']}`")

        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.history = []
            st.rerun()

# Main Chat UI
st.title("🤖 FinSolve AI Assistant")
st.caption("Ask role-aware questions about your company documents.")

if st.session_state.user:
    # One-time greeting
    if not st.session_state.history:
        st.session_state.history.append((
            "init",
            "Hello! I’m your AI assistant. What can I do for you today?"
        ))

    # Role explanation accordion
    with st.expander("📘 Access Policy", expanded=False):
        role = st.session_state.user["role"].lower()
        if "c-levelexecutives" in role:
            st.info("You have full visibility (C-Level Executives).")
        elif "employee" in role:
            st.info("You can only access general documents (Employee).")
        else:
            st.info(f"Access restricted to `{role}` department documents.")

    # Display past conversation (last 10 messages)
    for i, (q, a) in enumerate(st.session_state.history[-10:]):
        if q == "init":
            with st.chat_message("ai"):
                st.markdown(a)
        else:
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("ai"):
                st.markdown(a)

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"👍 Helpful {i}", key=f"yes_{i}"):
                        st.toast("Thanks for the feedback!", icon="✅")
                with c2:
                    if st.button(f"👎 Not Helpful {i}", key=f"no_{i}"):
                        st.toast("Got it, I’ll improve!", icon="⚠️")

    # Chat input box
    prompt = st.chat_input("💬 Type your question here")
    if prompt:
        st.chat_message("user").markdown(prompt)

        with st.chat_message("ai"):
            with st.spinner("Thinking..."):
                try:
                    res = requests.post(
                        "http://127.0.0.1:8000/chat",
                        json={"user": st.session_state.user, "message": prompt}
                    )
                    if res.status_code == 200:
                        reply = res.json().get("response", "⚠️ No reply.")

                        # Typewriter animation
                        out, container = "", st.empty()
                        for w in reply.split():
                            out += w + " "
                            container.markdown(out)
                            time.sleep(0.02)

                        st.session_state.history.append((prompt, reply))
                    else:
                        st.error("❌ Server returned an error.")
                except Exception as err:
                    st.error(f"🚫 Request failed: {err}")

else:
    st.info("🔑 Please log in from the sidebar to start chatting.")
