import streamlit as st
import cohere
import requests
from bs4 import BeautifulSoup  # Parses HTML for scraping text from web pages.
import tiktoken  # Utility to count tokens (text fragments) for OpenAI models.
from openai import OpenAI
import google.generativeai as genai

# Function to read webpage content from a URL
def read_webpage_from_url(url):
    try:
        response = requests.get(url)  # Get the URL
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        document = " ".join([p.get_text() for p in soup.find_all("p")])  # Extracts text inside <p> tags (paragraphs) and combines it into a single string
        return document
    except requests.RequestException as e:
        st.error(f"Error reading webpage from {url}: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing the webpage: {e}")  # Returns the combined text or an error message if fetching or processing fails
        return None

# Function to calculate tokens - It ensures that LLM interactions do not exceed model token limits.
def calculate_tokens(messages):
    """Calculate total tokens for a list of messages."""
    total_tokens = 0
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    for msg in messages:
        total_tokens += len(encoding.encode(msg['content']))
    return total_tokens

def truncate_messages_by_tokens(messages, max_tokens):  # This function reduces the message history if the total token count exceeds the specified max_tokens. Old messages are removed until the token limit is met.
    """Truncate the message buffer to ensure it stays within max_tokens."""
    total_tokens = calculate_tokens(messages)
    while total_tokens > max_tokens and len(messages) > 1:
        messages.pop(0)
        total_tokens = calculate_tokens(messages)
    return messages

# Function to verify OpenAI API key
def verify_openai_key(api_key):  # Verifies the OpenAI API key by trying to list available models. Returns a client object if successful.
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
        return client, True, "API key is valid"
    except Exception as e:
        return None, False, str(e)

# Function to generate summary using OpenAI
def generate_openai_response(client, messages, model): 
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        return stream
    except Exception as e:
        st.error(f"Error generating response: {e}", icon="❌")
        return None

def verify_cohere_key(api_key):  # Verifies the Cohere API key by running a small prompt and checking if the client works.
    try:
        client = cohere.Client(api_key)
        client.generate(prompt="Hello", max_tokens=5)
        return client, True, "API key is valid"
    except Exception as e:
        return None, False, str(e)

# Function to generate response using Cohere
def generate_cohere_response(cohere, messages):
    try:
        stream = client.chat_stream(
            model='command-r',
            message=messages[-1]['content'],
            chat_history=[{"role": m['role'], "message": m['content']} for m in messages[:-1]],
            temperature=0,       
            max_tokens=1500
        )
        return stream
    except Exception as e:
        st.error(f"Error generating response: {e}", icon="❌")
        return None

# Function to verify Gemini API key
def verify_gemini_key(api_key):
    try:
        genai.configure(api_key=api_key)
        client = genai.GenerativeModel('gemini-pro')
        return client, True, "API key is valid"
    except Exception as e:
        return None, False, str(e)

# Function to generate response using Gemini
def generate_gemini_response(client, messages, prompt):
    try:
        msgs = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            msgs.append({"role": role, "parts": msg["content"]})
        response = client.generate_content(
            contents=[*msgs, {"role": "user", "parts": [{"text": prompt}]}],
            generation_config=genai.types.GenerationConfig(
                temperature=0,
                max_output_tokens=1500,
            ),
            stream=True
        )
        return response
    except Exception as e:
        return None

# Summarizes the conversation differently based on the selected LLM provider: Gemini, OpenAI, or Cohere.
def generate_conversation_summary(client, messages, llm_provider):
    if llm_provider == 'Gemini':
        msgs = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            msgs.append({"role": role, "parts": [{"text": msg["content"]}]}])
        prompt = {"role": "user", "parts": [{"text": "Summarize the key points of this conversation concisely:"}]}
        response = client.generate_content(
            contents=[prompt, *msgs],
            generation_config=genai.types.GenerationConfig(
                temperature=0,
                max_output_tokens=150,
            ),
        )
        return response.text
    elif "OpenAI" in llm_provider:
        summary_prompt = "Summarize the key points of this conversation concisely:"
        for msg in messages:
            summary_prompt += f"\n{msg['role']}: {msg['content']}"
        response = client.chat.completions.create(
            model="gpt-4o-mini" if llm_provider == "OpenAI GPT-4O-Mini" else "gpt-4o",
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content
    else:  # Cohere
        summary_prompt = "Summarize the key points of this conversation concisely:"
        chat_history = []
        for msg in messages:
            chat_history.append({"role": msg['role'], "message": msg['content']})
            summary_prompt += f"\n{msg['role']}: {msg['content']}"
        response = client.chat(
            model='command-r',
            message=summary_prompt,
            chat_history=chat_history,
            temperature=0,       
            max_tokens=150
        )
        return response.text

st.title("Karan Shah 📄 Chatbot Interaction")
st.write("Interact with the chatbot! ")

# Sidebar: URL inputs
st.sidebar.header("URL Inputs")
url1 = st.sidebar.text_input("Enter the first URL:")
url2 = st.sidebar.text_input("Enter the second URL (optional):")

# Sidebar: LLM provider selection
st.sidebar.header("LLM Provider")
llm_provider = st.sidebar.selectbox(
    "Choose your LLM provider:",
    options=["OpenAI GPT-4O-Mini", "OpenAI GPT-4O", "Cohere", "Gemini"]
)

# Sidebar: Conversation memory type
st.sidebar.header("Conversation Memory")
memory_type = st.sidebar.radio(
    "Choose conversation memory type:",
    options=["Buffer of 5 questions", "Conversation summary", "Buffer of 5,000 tokens"]
)

# API key verification
if "OpenAI" in llm_provider:
    openai_api_key = st.secrets['openai']
    client, is_valid, message = verify_openai_key(openai_api_key)
    model = "gpt-4o-mini" if llm_provider == "OpenAI GPT-4O-Mini" else "gpt-4o"
elif "Cohere" in llm_provider:
    cohere_api_key = st.secrets['cohere']
    client, is_valid, message = verify_cohere_key(cohere_api_key)
else:
    gemini_api_key = st.secrets['gemini']
    client, is_valid, message = verify_gemini_key(gemini_api_key)

if is_valid:
    st.sidebar.success(f"{llm_provider} API key is valid!", icon="✅")
else:
    st.sidebar.error(f"Invalid {llm_provider} API key: {message}", icon="❌")
    st.stop()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Condition to check if at least one URL is provided
if not url1 and not url2:
    st.sidebar.warning("Please provide at least one URL to interact with the chatbot.")
    st.stop()  # Stop the execution if no URL is provided

# Process URLs
documents = []
if url1:
    doc1 = read_webpage_from_url(url1)
    if doc1:
        documents.append(doc1)
if url2:
    doc2 = read_webpage_from_url(url2)
    if doc2:
        documents.append(doc2)

# Combine documents
combined_document = "\n\n".join(documents)

# Display chat history
for message in st.session_state.messages:
    role = "user
