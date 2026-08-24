import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

def check_high_risk_message(message):
    """
    Detect potentially high-risk messages.
    """

    high_risk_keywords = [
        "suicide",
        "kill myself",
        "end my life",
        "self harm",
        "hurt myself",
        "want to die",
        "no reason to live",
        "harm someone",
        "kill someone"
    ]

    message = message.lower()

    return any(keyword in message for keyword in high_risk_keywords)

def get_safety_response():
    return """
I'm concerned about what you've shared.

If you feel that you might harm yourself or someone else, or if you're in immediate danger, please contact your local emergency services or a crisis support service right away.

Consider reaching out to:
- A trusted friend or family member
- A mental health professional
- A local emergency service if you are in immediate danger

You don't have to handle this alone.

Can you tell me whether you are currently safe?
"""

# -----------------------------------
# Load environment variables
# -----------------------------------

load_dotenv()

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found. Please check your .env file.")
    st.stop()

# Create Gemini client
client = genai.Client(api_key=api_key)


# -----------------------------------
# Mental Wellness Assistant
# -----------------------------------

system_instruction = """
You are an AI Mental Wellness Assistant.

Your purpose is to provide supportive, respectful, and general
mental wellness guidance.

Rules:

1. Be empathetic, calm, respectful, and non-judgmental.
2. Listen carefully to what the user is expressing.
3. Provide practical and healthy coping suggestions when appropriate.
4. Encourage healthy habits such as sleep, relaxation, exercise,
   social connection, and manageable routines.
5. Do not diagnose mental health conditions.
6. Do not claim to be a doctor, therapist, psychologist,
   or other healthcare professional.
7. Do not recommend prescription medicines or tell users to
   change medication.
8. Do not make the user dependent on the AI.
9. Encourage professional support when concerns are serious,
   persistent, or significantly affecting daily life.
10. If the user indicates immediate danger or possible harm to
    themselves or someone else, prioritize immediate safety and
    encourage contacting local emergency services, a crisis
    service, or a trusted person who can stay with them.
11. Never provide instructions for self-harm or violence.
12. Give detailed and helpful responses when the user's question requires explanation.
13. For simple questions, answer briefly. For complex questions, provide a structured,
step-by-step explanation with examples when useful.
14. Do not unnecessarily limit the response length.
15. Do not judge, shame, or dismiss the user's feelings.
16. Ask gentle follow-up questions when appropriate.
17. Never provide instructions, encouragement, or methods for self-harm, suicide, or violence.

18. If a user expresses thoughts of self-harm, suicide, or harming others, focus on immediate safety and encourage contacting emergency services, crisis support, or a trusted person.

19. Do not minimize or dismiss expressions of distress.

You are a wellness support assistant, not a replacement
for professional mental healthcare.
"""


# -----------------------------------
# Page configuration
# -----------------------------------

st.set_page_config(
    page_title="AI Mental Wellness Assistant",
    page_icon="🧠",
    layout="centered"
)


# -----------------------------------
# Sidebar
# -----------------------------------

with st.sidebar:

    st.header("🧠 About the Assistant")

    st.write(
        "This AI assistant provides general mental wellness "
        "conversation."
    )

    st.divider()

    st.subheader("Features")

    st.write("💬 Conversational chat")
    st.write("🧠 Mental wellness guidance")
    st.write("🤝 Supportive responses")
    st.write("📝 Conversation memory")

    st.divider()

    st.caption(
        "For educational purposes only."
    )


# -----------------------------------
# Main title
# -----------------------------------

st.title("🧠 AI Mental Wellness Assistant")

# -----------------------------------
# Mood Selection
# -----------------------------------

st.subheader("😊 How are you feeling today?")

mood = st.selectbox(
    "Select your current mood:",
    [
        "😊 Happy",
        "🙂 Good",
        "😐 Okay",
        "😟 Worried",
        "😰 Stressed",
        "😔 Sad",
        "😡 Angry",
        "😴 Tired"
    ]
)

st.write(
    "A supportive AI assistant for general mental wellness "
    "guidance and everyday emotional concerns."
)

st.info(
    "⚠️ This assistant provides general wellness support and "
    "does not replace professional mental healthcare."
)


# -----------------------------------
# Initialize chat history
# -----------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------------
# Display previous messages
# -----------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# -----------------------------------
# User input
# -----------------------------------

user_message = st.text_area(
    "How are you feeling today?",
    placeholder="Type your message here...",
    height=120
)

send_button = st.button("📤 Send", type="primary")


# -----------------------------------
# Generate response
# -----------------------------------

if send_button:

    if not user_message.strip():

        st.warning("Please enter a message first.")

    else:

        # Check for high-risk message first
        if check_high_risk_message(user_message):

            assistant_response = get_safety_response()

            # Save user message
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_message
                }
            )

            # Save safety response
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_response
                }
            )

            # Display response
            with st.chat_message("assistant"):
                st.markdown(assistant_response)

        else:

            # Save user message
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_message
                }
            )

            # Create conversation
            conversation = []

            # Add mood
            conversation.append(
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"My current mood is: {mood}"
                        }
                    ]
                }
            )

            # Add chat history
            for message in st.session_state.messages:

                # Gemini expects model instead of assistant
                role = (
                    "model"
                    if message["role"] == "assistant"
                    else "user"
                )

                conversation.append(
                    {
                        "role": role,
                        "parts": [
                            {
                                "text": message["content"]
                            }
                        ]
                    }
                )

            # Generate AI response
            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    try:

                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=conversation,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction
                            )
                        )

                        assistant_response = response.text

                        if assistant_response:
                            st.markdown(assistant_response)

                        else:
                            assistant_response = (
                                "I'm sorry, I couldn't generate a response."
                            )

                            st.warning(assistant_response)

                    except Exception as e:

                        assistant_response = (
                            "Sorry, I was unable to generate a response."
                        )

                        st.error(assistant_response)
                        st.exception(e)

            # Save assistant response
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_response
                }
            )


# -----------------------------------
# Clear chat
# -----------------------------------

if st.session_state.messages:

    if st.button("🗑️ Clear Chat",
    use_container_width=True):

        st.session_state.messages = []

        st.rerun()