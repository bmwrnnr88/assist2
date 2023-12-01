import openai
import streamlit as st
from bs4 import BeautifulSoup
import requests
import pdfkit
import time

# Initialize the OpenAI client with API key and Assistant ID from secrets.toml
openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]

client = openai

# Initialize session state variables for chat control
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Set up the Streamlit page with a title and icon
st.set_page_config(page_title="ChatGPT-like Chat App", page_icon=":speech_balloon:")

# Main chat interface setup
st.title("OpenAI Assistants API Chat")
st.write("This is a simple chat application that uses OpenAI's API to generate responses.")

# Button to start the chat session
if st.button("Start Chat"):
    st.session_state.start_chat = True
    # Initialize a thread for the chat session if it hasn't been done yet
    if "thread_id" not in st.session_state or st.session_state.thread_id is None:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

# Only show the chat interface if the chat has been started and a valid thread ID exists
if st.session_state.start_chat and st.session_state.thread_id:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-1106-preview"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for the user
    if prompt := st.chat_input("What is up?"):
        # Add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add the user's message to the existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Create a run with additional instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions="Please answer the queries using the knowledge provided in the files. When adding other information mark it clearly as such."
        )

        # Poll for the run to complete and retrieve the assistant's messages
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        # Retrieve messages added by the assistant
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            # Process the message (assuming you have a function for this)
            full_response = process_message_with_citations(message)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            with st.chat_message("assistant"):
                st.markdown(full_response, unsafe_allow_html=True)
else:
    # Prompt to start the chat
    st.write("Click 'Start Chat' to begin the conversation.")
