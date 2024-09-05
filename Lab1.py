import streamlit as st
from Lab1 import validate_api_key, generate_response

# Show title and description.
st.title("📄 My Document Question Answering - Lab 1")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# Initialize session state for API key validation
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False

# Fetch the API key from Streamlit secrets
openai_api_key = st.secrets["somesection"]  # Ensure this is set in .streamlit/secrets.toml

# Validate API key as soon as it is fetched
if openai_api_key:
    if validate_api_key(openai_api_key):
        st.success("API key is valid!")
        st.session_state.api_key_valid = True
    else:
        st.error("Invalid API key. Please check your OpenAI API key.")
        st.session_state.api_key_valid = False
else:
    st.error("API key not found in secrets!")

# Create an OpenAI client if the API key is valid
if st.session_state.api_key_valid:
    # Let the user upload a file via st.file_uploader
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )

    # Ask the user for a question via st.text_area
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        # Process the uploaded file and question
        document = uploaded_file.read().decode("utf-8")
        response = generate_response(openai_api_key, document, question)
        st.write(response)
else:
    st.info("Please add your OpenAI API key to continue.", icon="🗝")
