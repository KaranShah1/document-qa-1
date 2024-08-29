import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("📄 My Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via st.text_input.
# Alternatively, you can store the API key in ./.streamlit/secrets.toml and access it
# via st.secrets, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")

# if not openai_api_key:
#     st.info("Please add your OpenAI API key to continue.", icon="🗝")
# else:

#     # Create an OpenAI client.
#     client = OpenAI(api_key=openai_api_key)

#     # Let the user upload a file via st.file_uploader.
#     uploaded_file = st.file_uploader(
#         "Upload a document (.txt or .md)", type=("txt", "md")
#     )
##TEST WORKING ABOVE

##TEST START
# Function to validate the API key
def validate_api_key(api_key):
    try:
        client = OpenAI(api_key=api_key)
        client.Model.list()  # Example API call to validate the key
        return True
    except error.OpenAIError:
        return False

# Check if the user has entered an API key
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝")
else:
    # Validate the API key
    if validate_api_key(openai_api_key):
        st.success("API key validated successfully!")

        # Create an OpenAI client.
        client = OpenAI(api_key=openai_api_key)

        # Let the user upload a file via st.file_uploader.
        uploaded_file = st.file_uploader(
            "Upload a document (.txt or .md)", type=("txt", "md")
        )


    ##TEST END

    # Ask the user for a question via st.text_area.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:

        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            # model="gpt-3.5-turbo",
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using st.write_stream.
        st.write_stream(stream)
