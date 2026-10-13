
import streamlit as st
import pandas as pd
from gemma_assistant import ask_gemma

st.set_page_config(
    page_title="Kasuwa AI",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ Kasuwa AI")
st.subheader("Less guesswork. Smarter stocking.")

st.write(
    "Your AI-powered business assistant for understanding "
    "sales and making smarter restocking decisions."
)

st.divider()

st.header("1. Your Business")

budget = st.number_input(
    "How much money do you have for restocking? (₦)",
    min_value=0.0,
    value=10000.0,
    step=500.0
)

uploaded_file = st.file_uploader(
    "Upload your sales records (CSV or Excel)",
    type=["csv", "xlsx", "xls"]
)


business_context = (
    f"The trader's available restocking budget is ₦{budget:,.2f}."
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
    sales_data = pd.read_csv(uploaded_file)
else:
    sales_data = pd.read_excel(uploaded_file)

        st.success("Sales records uploaded successfully!")

        st.write("Preview of your records")
        st.dataframe(
            sales_data.head(10),
            use_container_width=True
        )

        st.metric("Total records", len(sales_data))
        st.write("Available columns:", ", ".join(sales_data.columns))

        # Summarise the uploaded data for the AI
        summary = sales_data.head(100).to_csv(index=False)

        business_context += (
            "\nUploaded CSV columns: "
            + ", ".join(sales_data.columns)
            + "\nSample of uploaded sales records:\n"
            + summary
        )

    except Exception as error:
        st.error(f"Could not read the CSV file: {error}")
        business_context = (
            f"The trader has a restocking budget of ₦{budget:,.2f}, "
            "but their uploaded file could not be read."
        )

st.divider()

st.header("2. Ask Kasuwa AI")

question = st.text_area(
    "What would you like help with?",
    placeholder=(
        "Example: What information do I need to decide "
        "which products to restock?"
    )
)

if st.button("Ask Kasuwa AI", type="primary"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Kasuwa AI is thinking..."):
            answer = ask_gemma(
                question,
                business_context
            )

        st.markdown("### Kasuwa AI's Response")
        st.write(answer)

st.caption(
    "Kasuwa AI is under development. "
    "Verify recommendations before making purchasing decisions."
)
