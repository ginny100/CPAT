import base64
import streamlit as st
import requests
import uuid
from io import BytesIO

st.set_page_config(layout="wide")

# Set up the Streamlit interface
st.title("Multimodal Video Generator")
page = st.markdown("""
    Welcome to the Multimodal Video Generator! 🚀
""")

# Generate a random session ID
session_id = str(uuid.uuid4())

# Initialize the session state for the backend URL
if "video_flask_api_url" not in st.session_state:
    st.session_state.video_flask_api_url = None

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
        st.session_state.video_flask_api_url = "{}/generate_video".format(link)  # Update ngrok URL
        st.rerun()  # Re-run the app to close the dialog

# Display the setup option if the URL is not set
if st.session_state.video_flask_api_url is None:
    setup_backend()

# Once the URL is set, display it or proceed with other functionality
if st.session_state.video_flask_api_url:
    st.success(f"Backend is set to: {st.session_state.video_flask_api_url}")

# Separate input for image upload
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# Display the uploaded image with width 400
if uploaded_file is not None:
    st.image(uploaded_file, width=400)

# Get prompt
user_prompt = st.text_input("Enter a prompt")
negative_prompt = st.text_input("Enter a negative prompt (optional)")

button = st.button("Generate Video")

# Process inputs only if both are provided
if user_prompt and uploaded_file and button:
    # Prepare the data for the request
    files = {'image': uploaded_file}
    data = {
        'prompt': user_prompt,
        'negative_prompt': negative_prompt if negative_prompt else ""
    }
    
    # Send the POST request to the Flask API
    response = requests.post(st.session_state.video_flask_api_url, files=files, data=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Save the response content to a local GIF file for debugging
        gif_path = f"generated_video_{session_id}.gif"
        with open(gif_path, "wb") as f:
            f.write(response.content)
        # Display the saved GIF file for verification
        file_ = open(gif_path, "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()

        st.markdown(
            f'<img src="data:image/gif;base64,{data_url}" alt="generated gif" width=50%>',
            unsafe_allow_html=True,
        )
        
        # Optional: Provide download link for the saved GIF
        st.markdown(f"Download generated GIF: [{gif_path}]({gif_path})")

    else:
        st.error(f"Error: {response.status_code}")
