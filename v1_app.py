import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Escape Room - V1 (Naive)", page_icon="🗝️")
st.title("🗝️ AI Escape Room: The Locked Study (V1)")
st.caption("Version 1: Pure LLM Game Master (Vulnerable to Hallucination & Prompt Injections)")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")

if not api_key:
    st.warning("Please enter your Gemini API Key to proceed.")
    st.stop()

SYSTEM_PROMPT = """
You are the Game Master of a text-based escape room.
The player wakes up in an old locked library.
Room elements:
1. Desk: Contains a locked wooden drawer with a 4-digit numeric keypad.
2. Bookshelf: Has four distinct books labeled with historical years (1, 9, 8, 4).
3. Painting: Shows a clock frozen at 19:84.
4. Drawer: Locked. The code is 1984. Inside is a brass exit key.
5. Exit Door: Heavy iron door locked with a brass key.

Rules:
- Describe what the player sees concisely.
- Do not let the player leave until the door is unlocked with the brass key.
- The player must find the code 1984 to open the drawer and get the key.
"""

if "v1_messages" not in st.session_state:
    st.session_state.v1_messages = [
        {"role": "assistant", "content": "You awaken inside a dimly lit library. The heavy iron exit door is locked shut. Around you, you see a wooden desk, a massive bookshelf, and an antique painting on the wall. What do you do?"}
    ]

for msg in st.session_state.v1_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("What do you do? (e.g., Examine the bookshelf)")

if user_input:
    st.session_state.v1_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    full_prompt = f"{SYSTEM_PROMPT}\n\nChat History:\n"
    for m in st.session_state.v1_messages:
        full_prompt += f"{m['role'].upper()}: {m['content']}\n"
    full_prompt += "ASSISTANT:"

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [{"text": full_prompt}]
                    }
                ]
            }
            try:
                res = requests.post(url, json=payload, timeout=20)
                data = res.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    reply = data["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(reply)
                    st.session_state.v1_messages.append({"role": "assistant", "content": reply})
                elif "error" in data:
                    st.error(f"Google API Error: {data['error'].get('message')}")
                else:
                    st.error(f"Unexpected response: {data}")
            except Exception as e:
                st.error(f"Connection error: {e}")

if st.sidebar.button("Restart Game"):
    st.session_state.v1_messages = []
    st.rerun()