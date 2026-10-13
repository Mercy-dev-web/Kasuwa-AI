
import requests
import streamlit as st

MODEL_ID = "openrouter/free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_gemma(question, business_context=""):
    """Ask an open-weight AI model to help a small business owner."""

    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        return "OpenRouter API key is missing from Streamlit Secrets."

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
                            "You are Kasuwa AI, a helpful assistant for "
                            "small business owners. Explain sales and "
                            "restocking decisions simply. Use only the "
                            "provided information. Never invent figures. "
                            "If information is missing, say so."
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
                f"OpenRouter error {response.status_code}: "
                f"{response.text[:500]}"
            )

        
data = response.json()
choices = data.get("choices", [])

if not choices:
    return f"No answer returned. Response: {str(data)[:1000]}"

choice = choices[0]
message = choice.get("message", {})
content = message.get("content")

if isinstance(content, str) and content.strip():
    return content

if isinstance(content, list):
    parts = []
    for item in content:
        if isinstance(item, dict) and item.get("text"):
            parts.append(item["text"])
    if parts:
        return "\n".join(parts)

if message.get("reasoning"):
    return (
        "The model returned reasoning but no final answer. "
        "Please try again or use another model."
    )

return (
    "The provider returned no readable text. "
    f"Finish reason: {choice.get('finish_reason')}. "
    f"Message fields: {list(message.keys())}. "
    f"Response fields: {list(data.keys())}."
)

        choices = data.get("choices", [])

        if not choices:
            return "The AI provider returned no answer. Please try again."

        message = choices[0].get("message", {})
        content = message.get("content")

        if isinstance(content, str) and content.strip():
            return content

        return (
            "The AI provider returned an empty answer. "
            "Please try again."
        )

    except requests.RequestException as error:
        return f"Could not connect to OpenRouter: {error}"
    except (ValueError, TypeError, KeyError) as error:
        return f"Could not read the AI response: {error}"
