
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
    "Upload your sales records or photos of your sales book",
    type=["csv", "xlsx", "xls", "docx", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    help="Upload spreadsheets or up to 15 photos of your sales book."
)

if uploaded_file and len(uploaded_file) > 8:
    st.warning("Please upload a maximum of 8 files.")
    uploaded_file = None


business_context = (
    f"The trader's available restocking budget is ₦{budget:,.2f}."
)

if uploaded_file is not None:
    try:
        if uploaded_file:
    try:
        dataframes = []

        for file in uploaded_file:
            filename = file.name.lower()

            if filename.endswith(".csv"):
                df = pd.read_csv(file)
            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file)
            elif filename.endswith(".docx"):
                st.info(
                    f"{file.name}: Word documents need "
                    "a separate text-reading step."
                )
                continue
            elif filename.endswith((".png", ".jpg", ".jpeg")):
                st.info(
                    f"{file.name}: Photo uploaded. "
                    "Image reading will be added next."
                )
                continue
            else:
                continue

            df["source_file"] = file.name
            dataframes.append(df)

        if dataframes:
            sales_data = pd.concat(
                dataframes,
                ignore_index=True
            )

            st.success("Sales records processed successfully!")

            st.write("Preview of your records")
            st.dataframe(
                sales_data.head(10),
                use_container_width=True
            )

            st.metric("Total records", len(sales_data))
            st.write(
                "Available columns:",
                ", ".join(map(str, sales_data.columns))
            )
        else:
            st.warning(
                "No spreadsheet records found yet. "
                "Photos are accepted, but image reading "
                "has not been connected."
            )

    except Exception as e:
        st.error(f"Could not process the uploaded files: {e}")


        summary = sales_data.head(100).to_csv(index=False)

        business_context += (
            "\nUploaded file columns: "
            + ", ".join(map(str, sales_data.columns))
            + "\nSample of uploaded sales records:\n"
            + summary
        )

    except Exception as error:
        st.error(f"Could not read the uploaded file: {error}")

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
