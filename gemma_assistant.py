import streamlit as st
from huggingface_hub import InferenceClient


MODEL_ID = "google/gemma-2-2b-it"


def ask_gemma(question, business_context=""):
    """Ask Gemma a question about a small business."""

    try:
        token = st.secrets["HF_TOKEN"]
    except (KeyError, FileNotFoundError):
        return (
            "Gemma is not connected yet. "
            "Please configure the Hugging Face token."
        )

    try:
        client = InferenceClient(
            model=MODEL_ID,
            token=token,
        )

        response = client.chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Kasuwa AI, a helpful business "
                        "assistant for small business owners. "
                        "Explain sales patterns and stocking decisions "
                        "in simple language. Use only the information "
                        "provided. Never invent sales figures, costs, "
                        "or stock levels. If information is missing, "
                        "say so clearly."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Business information:\n{business_context}\n\n"
                        f"Trader's question:\n{question}"
                    ),
                },
            ],
            max_tokens=300,
            temperature=0.3,
        )

        return response.choices[0].message.content

    except Exception as error:
        return (
            "I couldn't get a response from Gemma. "
            "Please check the model access, token, and connection. "
            f"Technical detail: {error}"
        )
