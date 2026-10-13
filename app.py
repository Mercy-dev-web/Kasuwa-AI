import streamlit as st
import pandas as pd
from gemma_assistant import ask_gemma

st.set_page_config(
    page_title="Kasuwa AI",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ Kasuwa AI")
st.subheader("Your AI business assistant")

st.write(
    "Understand your sales, manage your stock, "
    "and make smarter restocking decisions."
)

st.divider()

# Business budget
st.header("💰 Your Restocking Budget")

budget = st.number_input(
    "How much money do you have for restocking? (₦)",
    min_value=0,
    value=10000,
    step=1000
)

st.divider()

# Upload sales records
st.header("📒 Your Sales Records")

st.write(
    "Upload your sales spreadsheet or select photos "
    "of your handwritten sales book."
)

uploaded_files = st.file_uploader(
    "Upload spreadsheets or up to 15 photos",
    type=["csv", "xlsx", "xls", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    help="You can select multiple files at once."
)

if uploaded_files and len(uploaded_files) > 15:
    st.warning("Please upload a maximum of 15 files.")
    uploaded_files = []

# Camera feature for mobile users
st.subheader("📸 Take a Photo of Your Sales Book")

camera_photo = st.camera_input(
    "Take a picture of a page"
)

if camera_photo is not None:
    st.success("Photo captured successfully!")
    st.image(
        camera_photo,
        caption="Captured sales book page",
        use_container_width=True
    )
    st.info(
        "Your photo has been captured. "
        "Reading the figures from photos is not connected yet."
    )

# Process uploaded files
dataframes = []
image_files = []

if uploaded_files:
    for file in uploaded_files:
        filename = file.name.lower()

        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(file)
                df["source_file"] = file.name
                dataframes.append(df)

            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file)
                df["source_file"] = file.name
                dataframes.append(df)

            elif filename.endswith((".png", ".jpg", ".jpeg")):
                image_files.append(file)

        except Exception as error:
            st.error(
                f"Could not read {file.name}: {error}"
            )

if image_files:
    st.success(
        f"{len(image_files)} photo(s) uploaded successfully."
    )

    for image_file in image_files:
        st.image(
            image_file,
            caption=image_file.name,
            use_container_width=True
        )

    st.info(
        "Kasuwa AI can receive these photos, but we still "
        "need to connect handwriting recognition before "
        "it can extract your sales information."
    )

# Combine spreadsheet records
sales_data = None

if dataframes:
    sales_data = pd.concat(
        dataframes,
        ignore_index=True
    )

    st.success("Spreadsheet records processed successfully!")

    st.subheader("📊 Preview of Your Sales Records")

    st.dataframe(
        sales_data.head(10),
        use_container_width=True
    )

    st.metric(
        "Total records",
        len(sales_data)
    )

    st.write(
        "Available columns:",
        ", ".join(map(str, sales_data.columns))
    )

st.divider()

# AI assistant
st.header("🤖 Ask Kasuwa AI")

st.write(
    "Ask questions about your sales or how to use "
    "your restocking budget."
)

question = st.text_area(
    "What would you like to know?",
    placeholder=(
        "Example: Which products should I restock "
        "with my current budget?"
    )
)

if st.button("Ask Kasuwa AI", type="primary"):

    if not question.strip():
        st.warning("Please enter a question first.")

    else:
        # Build context for the AI
        business_context = (
            f"Restocking budget: ₦{budget:,.2f}\n"
        )

        if sales_data is not None:
            business_context += (
                "\nSales records:\n"
                + sales_data.head(50).to_string(index=False)
            )
        else:
            business_context += (
                "\nNo spreadsheet records have been processed. "
                "Do not invent sales figures."
            )

        with st.spinner("Kasuwa AI is thinking..."):
            answer = ask_gemma(
                question,
                business_context
            )

        st.subheader("💡 Kasuwa AI's Answer")
        st.write(answer)

st.divider()

st.caption(
    "Kasuwa AI — helping small business owners "
    "make smarter business decisions."
)
