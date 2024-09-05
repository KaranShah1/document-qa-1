import streamlit as st
import openai
from openai.error import OpenAIError

# Show title and description.
st.title("📄 My Document Question Answering - Lab 1")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# Initialize session state for API key validation
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False

# Function to validate the API key
def validate_api_key(api_key):
    try:
        # Set the OpenAI API key
        openai.api_key = api_key
        # Test the API key with a basic request
        openai.ChatCompletion.create(
            model="gpt-4.0-mini", messages=[{"role": "system", "content": "Hello"}]
        )
        return True
    except OpenAIError as e:
        st.error(f"Error validating API key: {e}")
        return False

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
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

        # Generate an answer using the OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.0-mini",
                messages=messages
            )
            st.write(response.choices[0].message['content'])
        except OpenAIError as e:
            st.error(f"An error occurred while generating the response: {e}")
else:
    st.info("Please add your OpenAI API key to continue.", icon="🗝")
