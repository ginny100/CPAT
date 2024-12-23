import streamlit as st
import requests
import uuid

st.set_page_config(layout="wide")

# Set up the Streamlit interface
st.title("Multimodal Caption Generator")
page = st.markdown("""
    Welcome to the Multimodal Caption Generator! 🚀
""")

# Generate a random session ID
session_id = str(uuid.uuid4())

# Initialize the session state for the backend URL
if "caption_flask_api_url" not in st.session_state:
    st.session_state.caption_flask_api_url = None

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
        st.session_state.caption_flask_api_url = "{}/caption".format(link)  # Update ngrok URL
        st.rerun()  # Re-run the app to close the dialog

# Display the setup option if the URL is not set
if st.session_state.caption_flask_api_url is None:
    setup_backend()

# Once the URL is set, display it or proceed with other functionality
if st.session_state.caption_flask_api_url:
    st.success(f"Backend is set to: {st.session_state.caption_flask_api_url}")

# Upload File
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Display the uploaded image with width 400
if uploaded_file is not None:
    st.image(uploaded_file, width=400)

# Get Prompt
user_prompt = st.text_input("Enter a prompt")

button = st.button("Generate Caption")

# Process inputs only if both are provided
if user_prompt and uploaded_file and button:
    # Prepare the data for the request
    files = {'image': uploaded_file}
    data = {'prompt': user_prompt}
    
    # Send prompt and image to server
    response = requests.post(st.session_state.caption_flask_api_url, files=files, data=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Get the response from the API
        api_response = response.json()
        generated_caption = api_response.get("response", "No caption received.")
        
        # Display the generated caption with enhanced formatting
        st.markdown(f"**Generated Caption:** {generated_caption}")
        
    else:
        st.error(f"Error: {response.status_code}")
