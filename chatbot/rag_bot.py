import streamlit as st
import json
import os
from groq import Groq
from dotenv import load_dotenv

# 1. Load Environment Variables (API Keys)
load_dotenv()

# 2. Setup the Groq Client (The Brain)
# Make sure GROQ_API_KEY is in your .env file!
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    st.error("❌ API Key missing! Check your .env file.")
    st.stop()

# --- HELPER FUNCTIONS ---


def load_data():
    """
    Reads the 'products.json' file from the 'data' folder.
    This is the file your partner (Member A) is responsible for filling.
    """
    file_path = os.path.join("data", "products.json")

    # Safety check: Does the file exist?
    if not os.path.exists(file_path):
        return []

    # Read the file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def generate_answer(query, products):
    """
    Feeds the user's question + product data to the LLM.
    """
    # 1. Prepare the "Context" (The Knowledge Base)
    # We turn the JSON list into a single string of text so the AI can read it.
    context_text = ""
    for p in products:
        context_text += (
            f"---\nURL: {p.get('url', 'N/A')}\nINFO: {p.get('content', '')}\n"
        )

    # 2. Create the Prompt
    system_prompt = f"""
    You are an expert E-commerce Shopping Assistant.
    
    YOUR KNOWLEDGE BASE:
    {context_text}
    
    INSTRUCTIONS:
    - Answer the user's question using ONLY the knowledge base above.
    - If the answer isn't in the data, say "I don't have that information in my current records."
    - Mention the "URL" if you are recommending a specific product.
    """

    # 3. Call Groq
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.1,  # Keep it factual
    )

    return completion.choices[0].message.content


# --- STREAMLIT UI (The Website) ---

st.set_page_config(page_title="Shopping Bot", page_icon="🛒")
st.title("🛒 E-Commerce Intelligence Bot")
st.caption("Powered by Groq & Llama 3")

# Sidebar: Debugging Info
with st.sidebar:
    st.header("System Status")
    products = load_data()
    if products:
        st.success(f"✅ Database Loaded: {len(products)} Items")
    else:
        st.warning("⚠️ Database is Empty or Missing")
        st.info("Waiting for scraper to run...")

# Main Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box
if prompt := st.chat_input("Ex: Which laptop has the best battery?"):
    # 1. Show User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generate Response
    if products:
        with st.spinner("Analyzing product reviews..."):
            response = generate_answer(prompt, products)
    else:
        response = "I cannot answer yet because the product database is empty. Please run the scraper first."

    # 3. Show AI Message
    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
