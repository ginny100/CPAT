import streamlit as st
import requests
import base64
import uuid

st.set_page_config(layout="wide")

# Set up the Streamlit interface
st.title("Image Generator")
page = st.markdown("""
    Welcome to the Image Generator! 🚀
""")

# Generate a random session ID
session_id = str(uuid.uuid4())

# Initialize the session state for the backend URL
if "img_flask_api_url" not in st.session_state:
    st.session_state.img_flask_api_url = None

# Function to display the dialog and set the URL
@st.dialog("Setup Back end")
def setup_backend():
    st.markdown(
        """
        Run [Image Generation Server](https://colab.research.google.com/drive/1pX-H3jojIzPmLxxcrGdLSwJvC8oe3dvM#scrollTo=m_W92R6c54lM) and paste the Ngrok link below.
        """
    )
    link = st.text_input("Backend URL", "")
    if st.button("Save"):
        st.session_state.img_flask_api_url = "{}/generate_image".format(link)  # Update ngrok URL
        st.rerun()  # Re-run the app to close the dialog

# Display the dialog only if the URL is not set
if st.session_state.img_flask_api_url is None:
    setup_backend()

# Once the URL is set, display it or proceed with other functionality
if st.session_state.img_flask_api_url:
    st.success(f"Backend is set to: {st.session_state.img_flask_api_url}")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Get Prompt
prompt = st.chat_input(key="chat", placeholder="Enter a prompt to generate an image")

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
            "prompt": prompt,
            "size": "1024x1024", # Default size, can be changed to user input
            "quality": "standard", # Default quality, can be changed to user input
            "n": 1,  # Default to 1 image, can be changed to user input
            "sessionId": session_id
        }
        
        # Send the POST request to the Flask API
        response = requests.post(st.session_state.img_flask_api_url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Get the response from the API
            api_response = response.json()
            
            # Assume api_response['b64_json'] is a list and we need the first item
            base64_image_string = api_response['b64_json'][0] if isinstance(api_response['b64_json'], list) else api_response['b64_json']
            
            # Decode the base64 image from the API response
            image_data = base64.b64decode(base64_image_string)
            
            # Display the image in Streamlit
            st.image(image_data, caption="Generated Image", use_container_width=True)
            st.info("Before entering a new prompt to generate another image, make sure to save the current image if needed.")
            
            # Add the assistant's response to the chat history
            st.session_state.chat_history.append({"role": "assistant", "content": "Image generated and displayed."})
        else:
            st.error(f"**Error Code:** {response.status_code}\n\n**Error Message:** {response.text}")