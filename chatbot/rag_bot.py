import streamlit as st
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    st.error("❌ API Key missing! Check your .env file.")
    st.stop()


def load_data():
    """
    Reads the 'products.json' file from the 'data' folder.
    """
    file_path = os.path.join("data", "products.json")

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def generate_answer(query, products):
    """
    Feeds the user's question + product data to the LLM.
    Includes a SAFETY LIMIT to prevent crashing the API.
    """

    context_text = ""

    MAX_CHARS = 15000

    for p in products:
        product_info = (
            f"---\nURL: {p.get('url', 'N/A')}\nINFO: {p.get('content', '')[:500]}\n"
        )
        if len(context_text) + len(product_info) < MAX_CHARS:
            context_text += product_info
        else:
            break

    system_prompt = f"""
    You are an expert E-commerce Shopping Assistant.
    
    YOUR KNOWLEDGE BASE:
    {context_text}
    
    INSTRUCTIONS:
    - Answer the user's question using ONLY the knowledge base above.
    - If the answer isn't in the data, say "I don't have that information in my current records."
    - Mention the "URL" if you are recommending a specific product.
    """

    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.1,
    )

    return completion.choices[0].message.content


st.set_page_config(page_title="Shopping Bot", page_icon="🛒")
st.title("E-Commerce Intelligence Bot")

with st.sidebar:
    st.header("System Status")
    products = load_data()
    if products:
        st.success(f"Database Loaded: {len(products)} Items")
    else:
        st.warning("Database is Empty or Missing")
        st.info("Waiting for scraper to run...")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Ex: Which laptop has the best battery?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if products:
        with st.spinner("Analyzing product reviews..."):
            response = generate_answer(prompt, products)
    else:
        response = "I cannot answer yet because the product database is empty. Please run the scraper first."

    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
