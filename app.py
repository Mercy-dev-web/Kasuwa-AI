import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Kasuwa AI",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ Kasuwa AI")
st.subheader("Your AI-powered business assistant")

st.write(
    "Make smarter stocking decisions using your sales records "
    "and available budget."
)

st.divider()

st.header("📊 Analyse Your Business")

budget = st.number_input(
    "What is your available restocking budget?",
    min_value=0.0,
    value=10000.0,
    step=500.0
)

uploaded_file = st.file_uploader(
    "Upload your sales records (CSV)",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        sales_data = pd.read_csv(uploaded_file)

        st.success("Sales records uploaded successfully!")

        st.write("Preview of your records:")
        st.dataframe(sales_data.head(10), use_container_width=True)

        st.metric(
            "Total records",
            len(sales_data)
        )

        st.info(
            "Next, Kasuwa AI will analyse your sales "
            "and recommend what to restock."
        )

    except Exception as error:
        st.error(f"Could not read the CSV file: {error}")

else:
    st.info(
        "Upload a CSV file to begin analysing your sales."
    )

st.divider()

st.caption(
    "Kasuwa AI | Less guesswork. Smarter stocking. Better decisions."
)
