import streamlit as st
import requests
import base64
import os
import json
from openai import OpenAI
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY"))

client = OpenAI()

# Function to process the document and get the summary
def get_document_text(encoded_content, access_token):
    payload = json.dumps({
        "skipHumanReview": True,
        "rawDocument": {
            "mimeType": "application/pdf",
            "content": encoded_content
        }
    })

    project_id = 'cwaipai'
    access_token = 'ya29.a0AfB_byDeDaYiGf3kXhXj2bJpDbi4yqlLllJ8O7HzVN89UWBKWmQG6I0_LaDwTj7pOZUqQCdRHQ4F5x4HNAU4PM1bFRubr8moOU51isaMA04iZAy8cNOcWDV1bSyf5TNQ2g9vaTE4i1OUNTla4mHSDncJxCtKd3Yj0NFYkwaCgYKAWgSARISFQHGX2MiBiSQ_NBqG1rbxgqYxWJesw0173'
    endpoint_url = f"https://us-documentai.googleapis.com/v1/projects/450368740110/locations/us/processors/44657797e61c9b6b:process"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    response = requests.post(endpoint_url, headers=headers, data=payload)
    
    if response.ok:
        response_json = response.json()
        # Assuming the text is in the 'text' field of the 'document' object
        text_content = response_json.get('document', {}).get('text', '')
        return text_content
    else:
        return f"Error: {response.status_code}, {response.text}"

def get_summary(text_content):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Please summarize the following housing contract using five lines (some of them can be bulleted):\n\n{text_content}"}
        ]
        summary_response = client.chat.completions.create(model="gpt-4-0125-preview", messages=messages)
        summary = summary_response.choices[0].message.content
        return summary
    except Exception as e:
        return f"OpenAI Error: {str(e)}"

def get_answer(question, text_content):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant helping students with their housing contracts."},
            {"role": "user", "content": f"Answer this question based on this housing contract in bullet points:\n\n{question}\n\nContext:\n{text_content}"}
        ]
        answer_response = client.chat.completions.create(model="gpt-4-0125-preview", messages=messages)
        answer = answer_response.choices[0].message.content

        return answer

    except Exception as e:
        return f"OpenAI Error: {str(e)}"

def get_answer_1(question, text_content):
    try:
        cloudflare_ai_url = "https://worker-purple-shape-6e9d.sohampatil-ai.workers.dev"

        payload = {
            "prompt": question,
            "context": text_content 
        }

        response = requests.post(cloudflare_ai_url, json=payload)

        # Check if the response is OK
        if response.ok:
            response_data = response.json()

            if isinstance(response_data, dict) and 'answer' in response_data:
                answer = response_data['answer']
            else:
                answer = "The response format is unexpected or an error occurred."
            
            return answer

        else:
            return f"Error: {response.status_code}, {response.text}"

    except Exception as e:
        return f"Cloudflare AI Error: {str(e)}"


st.set_page_config(layout="wide")

st.markdown("<h1 style='font-size:70px;'>RentRightly 🏠</h1>", unsafe_allow_html=True)

col1, spacer, col2 = st.columns([5, 1, 5])


with col1:
    st.header("Upload your contract here!")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    text_content = ""  # Initialize text_content here

    if uploaded_file is not None:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.markdown(f"<h3 style='font-size:16px;'>Preview: {uploaded_file.name}</h3>", unsafe_allow_html=True)
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{base64.b64encode(uploaded_file.getvalue()).decode()}" width="100%" height="800" type="application/pdf"></iframe>',
            unsafe_allow_html=True,
        )

        encoded_content = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        access_token = 'ya29.a0AfB_byDeDaYiGf3kXhXj2bJpDbi4yqlLllJ8O7HzVN89UWBKWmQG6I0_LaDwTj7pOZUqQCdRHQ4F5x4HNAU4PM1bFRubr8moOU51isaMA04iZAy8cNOcWDV1bSyf5TNQ2g9vaTE4i1OUNTla4mHSDncJxCtKd3Yj0NFYkwaCgYKAWgSARISFQHGX2MiBiSQ_NBqG1rbxgqYxWJesw0173'
        text_content = get_document_text(encoded_content, access_token)  # Update text_content here

# with spacer:
#     st.write("")

with col2:

    # Create a button to get the summary and check if the document is uploaded
    if uploaded_file is not None and text_content and not text_content.startswith("Error:"):
        if st.button('Get Contract Summary'):
            summary = get_summary(text_content)
            st.write(summary)
        else:
            st.write("")  


    st.header("Ask Me Anything!")
    # Store the question in a variable
    question = st.text_input("Ask a question based on your housing contract:")

    if st.button('Get Answer'):
            answer = get_answer(question, text_content)
            st.write(answer)
    else:
        if not uploaded_file:
            st.error("Please upload a document first.")