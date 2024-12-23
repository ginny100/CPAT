import streamlit as st
import requests
import uuid

st.set_page_config(layout="wide")

# Set up the Streamlit interface
st.title("LLMs Playground")
page = st.markdown("""
    Welcome to the Large Language Models Playground! 🚀
""")

# Generate a random session ID
session_id = str(uuid.uuid4())

# Initialize the session state for the backend URL
if "flask_api_url" not in st.session_state:
    st.session_state.flask_api_url = None

# Function to display the dialog and set the URL
@st.dialog("Setup Backend")
def setup_backend():
    st.markdown(
        """
        Run the [server](https://colab.research.google.com/drive/11FLH820TFiXSKA48uZbF6GdVB213JrAD#scrollTo=TqzJlsGZORDI) and paste the Ngrok link below.
        """
    )
    link = st.text_input("Backend URL", "")
    if st.button("Save"):
        st.session_state.flask_api_url = "{}/chat".format(link) # Update ngrok URL
        st.rerun()  # Re-run the app to close the dialog

# Display the setup option if the URL is not set
if st.session_state.flask_api_url is None:
    setup_backend()

# Once the URL is set, display it or proceed with other functionality
if st.session_state.flask_api_url:
    st.success(f"Backend is set to: {st.session_state.flask_api_url}")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Get Prompt
prompt = st.chat_input(key="chat", placeholder="Ask me something")

# Display the chat history using chat UI
col1, col3, col2 = st.columns([6, 0.1, 3])

with col1:
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare the payload for the request
        payload = {
            "message": {"content": prompt},
            "context": st.session_state.chat_history,
            "sessionId": session_id,
            "model": st.session_state.selected_model,
            "temperature": st.session_state.temperature,
            "top_p": st.session_state.top_p,
            "stream": True  # Enable streaming
        }

        # Stream the response from the Flask API
        with st.chat_message("assistant"):
            streamed_content = ""  # Initialize an empty string to concatenate chunks
            response = requests.post(st.session_state.flask_api_url, json=payload, stream=True)
            
            # Create a placeholder to update the markdown
            response_placeholder = st.empty()

            # Check if the request was successful
            if response.status_code == 200:
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        # print(chunk)
                        streamed_content += chunk
                        response_placeholder.markdown(streamed_content)

                # Once complete, add the full response to the chat history
                st.session_state.chat_history.append({"role": "assistant", "content": streamed_content})
            else:
                st.error(f"Error: {response.status_code}")

# Sidebar settings for model, temperature, and top_p
with st.sidebar:
    # LLM Model selection
    st.session_state.selected_model = st.selectbox(
        "Select Model",
        ("gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-4-mini")
    )
    st.write("You selected:", st.session_state.selected_model)

    # Temperature setting
    st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1)
    st.write("Current Temperature:", st.session_state.temperature)

    # Top p setting
    st.session_state.top_p = st.slider("Top p", 0.0, 1.0, 0.5, 0.1)
    st.write("Current Top p:", st.session_state.top_p)
