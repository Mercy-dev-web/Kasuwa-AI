import streamlit as st
from huggingface_hub import InferenceClient

MODEL_ID = "google/gemma-3-4b-it"


def ask_gemma(question, business_context=""):
    """Ask Gemma a question about a small business."""

    try:
        token = st.secrets["HF_TOKEN"]
    except Exception:
        return (
            "Gemma is not connected yet. "
            "Please check the HF_TOKEN secret in Streamlit Cloud."
        )

    try:
        client = InferenceClient(
            model=MODEL_ID,
            provider="auto",
            api_key=token,
        )

        response = client.chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Kasuwa AI, a helpful business assistant "
                        "for small business owners. Explain sales patterns "
                        "and stocking decisions in simple language. Use "
                        "only the information provided. Never invent sales "
                        "figures, costs, or stock levels. Clearly state "
                        "when information is missing."
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
            "Please check the Hugging Face token, model access, "
            "and inference provider settings. "
            f"Technical detail: {error}"
        )
