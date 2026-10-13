
import base64
import requests
import streamlit as st

MODEL_ID = "openrouter/free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"


def get_api_key():
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        return None


def get_message_text(message):
    content = message.get("content")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = [
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("text")
        ]
        return "\n".join(parts).strip()

    return ""


def ask_gemma(question, business_context=""):
    api_key = get_api_key()

    if not api_key:
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
                            "Clearly state when information is missing."
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
                "max_tokens": 800,
                "temperature": 0.3,
                "reasoning": {"effort": "low"},
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
            return "The AI provider returned no answer. Please try again."

        message = choices[0].get("message", {})
        content = get_message_text(message)

        if content:
            return content

        finish_reason = choices[0].get("finish_reason")
        return (
            "The provider returned no readable text. "
            f"Finish reason: {finish_reason}."
        )

    except requests.RequestException as error:
        return f"Could not connect to OpenRouter: {error}"
    except (ValueError, TypeError, KeyError) as error:
        return f"Could not read the AI response: {error}"


def extract_sales_from_images(images):
    api_key = get_api_key()

    if not api_key:
        return (
            '{"records": [], "notes": '
            '"OpenRouter API key is missing from Streamlit Secrets."}'
        )

    content = [
        {
            "type": "text",
            "text": (
                "Read the attached photos of a small business sales book. "
                "Extract every sales record that you can clearly read. "
                "Return ONLY valid JSON in this exact structure:\n"
                '{"records": [{"date": "", "product": "", '
                '"quantity": null, "unit_price": null, '
                '"total_amount": null}], "notes": ""}\n\n'
                "Rules:\n"
                "- Use the date as written; do not guess missing dates.\n"
                "- Quantity should be a number when clearly readable.\n"
                "- Prices and amounts should be numbers without currency "
                "symbols or commas.\n"
                "- Use null for figures you cannot confidently read.\n"
                "- Use an empty string for unreadable dates or products.\n"
                "- Do not calculate or invent missing figures.\n"
                "- Include unclear handwriting in notes.\n"
                "- If no records can be read, return an empty records list.\n"
                "- Do not include Markdown code fences."
            ),
        }
    ]

    for index, image_file in enumerate(images, start=1):
        try:
            image_bytes = image_file.getvalue()
            mime_type = getattr(image_file, "type", None)

            if mime_type not in ("image/jpeg", "image/png", "image/webp"):
                mime_type = "image/jpeg"

            encoded_image = base64.b64encode(image_bytes).decode("utf-8")

            content.append(
                {
                    "type": "text",
                    "text": f"Sales-book photo {index}:",
                }
            )

            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (
                            f"data:{mime_type};base64,{encoded_image}"
                        )
                    },
                }
            )

        except Exception as error:
            return (
                '{"records": [], "notes": '
                f'"Could not prepare photo {index}: {str(error)}"}}'
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
                        "role": "user",
                        "content": content,
                    }
                ],
                "max_tokens": 2500,
                "temperature": 0,
            },
            timeout=120,
        )

        if not response.ok:
            return (
                '{"records": [], "notes": '
                + repr(
                    f"OpenRouter error {response.status_code}: "
                    f"{response.text[:300]}"
                )
                + "}"
            )

        data = response.json()
        choices = data.get("choices", [])

        if not choices:
            return (
                '{"records": [], "notes": '
                '"The AI provider returned no answer. Please try again."}'
            )

        message = choices[0].get("message", {})
        result = get_message_text(message)

        if result:
            return result

        return (
            '{"records": [], "notes": '
            '"The AI returned no readable text. Please try again."}'
        )

    except requests.RequestException as error:
        return (
            '{"records": [], "notes": '
            + repr(f"Could not connect to OpenRouter: {error}")
            + "}"
        )
    except (ValueError, TypeError, KeyError) as error:
        return (
            '{"records": [], "notes": '
            + repr(f"Could not read the AI response: {error}")
            + "}"
        )
