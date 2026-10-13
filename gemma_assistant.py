import requests
import streamlit as st

MODEL_ID = "google/gemma-4-26b-a4b-it:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_gemma(question, business_context=""):
    """Ask Gemma to help a small business owner."""

    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        return (
            "OpenRouter is not configured. "
            "Check OPENROUTER_API_KEY in Streamlit Secrets."
        )

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-OpenRouter-Title": "Kasuwa AI",
            },
            json={
                "model": MODEL_ID,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are Kasuwa AI, a helpful business "
                            "assistant for small business owners. "
                            "Explain sales patterns and stocking "
                            "decisions in simple language. Use only "
                            "provided information. Never invent sales "
                            "figures, costs, or stock levels. If "
                            "information is missing, say so clearly."
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
                "max_tokens": 300,
                "temperature": 0.3,
            },
            timeout=60,
        )

        if not response.ok:
            return (
                f"OpenRouter returned error {response.status_code}: "
                f"{response.text[:500]}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.RequestException as error:
        return f"Could not connect to OpenRouter: {error}"
    except (KeyError, ValueError, TypeError) as error:
        return f"Unexpected response from the AI service: {error}"
