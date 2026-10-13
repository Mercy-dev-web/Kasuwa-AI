
import json
import re

import pandas as pd
import streamlit as st

from gemma_assistant import ask_gemma, extract_sales_from_images


st.set_page_config(
    page_title="Kasuwa AI",
    page_icon="🛍️",
    layout="wide",
)

st.title("🛍️ Kasuwa AI")
st.subheader("Less guesswork. Smarter stocking.")

st.write(
    "Your AI-powered business assistant for understanding "
    "sales and making smarter restocking decisions."
)

if "extracted_sales" not in st.session_state:
    st.session_state.extracted_sales = []

if "extraction_notes" not in st.session_state:
    st.session_state.extraction_notes = ""

if "extraction_raw" not in st.session_state:
    st.session_state.extraction_raw = ""


st.divider()
st.header("1. Your Business")

budget = st.number_input(
    "How much money do you have for restocking? (₦)",
    min_value=0.0,
    value=10000.0,
    step=500.0,
)

uploaded_files = st.file_uploader(
    "Upload sales spreadsheets or photos of your sales book",
    type=["csv", "xlsx", "xls", "png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
    help="Upload up to 8 files at a time.",
)

camera_photo = st.camera_input(
    "Or take a photo of a sales book page"
)

dataframes = []
image_files = []

if uploaded_files and len(uploaded_files) > 8:
    st.warning("Please upload a maximum of 8 files.")
else:
    for file in uploaded_files or []:
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

            elif filename.endswith(
                (".png", ".jpg", ".jpeg", ".webp")
            ):
                image_files.append(file)

        except Exception as error:
            st.error(f"Could not read {file.name}: {error}")

if camera_photo is not None:
    image_files.append(camera_photo)

if image_files:
    st.write(f"**Photos received:** {len(image_files)}")

    for index, image in enumerate(image_files, start=1):
        st.image(
            image,
            caption=getattr(image, "name", f"Sales photo {index}"),
            use_container_width=True,
        )

    if len(image_files) > 8:
        st.warning(
            "Please use a maximum of 8 photos at a time, "
            "including the camera photo."
        )
    else:
        if st.button(
            "Read My Sales Book",
            type="primary",
        ):
            with st.spinner(
                "Kasuwa AI is reading your sales book..."
            ):
                raw_result = extract_sales_from_images(image_files)

            st.session_state.extraction_raw = raw_result

            try:
                # Allow for a response wrapped in Markdown fences.
                cleaned = re.sub(
                    r"^\s*```(?:json)?\s*|\s*```\s*$",
                    "",
                    raw_result.strip(),
                    flags=re.IGNORECASE,
                )

                # Recover the JSON object if extra text surrounds it.
                start = cleaned.find("{")
                end = cleaned.rfind("}")

                if start != -1 and end > start:
                    cleaned = cleaned[start:end + 1]

                parsed = json.loads(cleaned)

                records = parsed.get("records", [])
                notes = parsed.get("notes", "")

                if not isinstance(records, list):
                    raise ValueError(
                        "The returned records were not in list format."
                    )

                st.session_state.extracted_sales = records
                st.session_state.extraction_notes = str(notes)

            except (json.JSONDecodeError, ValueError, TypeError):
                st.session_state.extracted_sales = []
                st.session_state.extraction_notes = (
                    "Kasuwa could not convert the response into a "
                    "usable table. See the raw response below."
                )

if st.session_state.extraction_notes:
    st.info(st.session_state.extraction_notes)

if st.session_state.extraction_raw and not st.session_state.extracted_sales:
    with st.expander("View the AI response"):
        st.text(st.session_state.extraction_raw)


# Combine any uploaded spreadsheets.
sales_data = None

if dataframes:
    sales_data = pd.concat(dataframes, ignore_index=True)

    st.success("Spreadsheet records processed successfully!")
    st.subheader("Spreadsheet preview")

    st.dataframe(
        sales_data.head(10),
        use_container_width=True,
    )

    st.metric("Spreadsheet records", len(sales_data))

# Display and allow correction of extracted handwriting.
reviewed_sales = None

if st.session_state.extracted_sales:
    st.divider()
    st.header("2. Review Your Sales Records")

    st.write(
        "Check the extracted figures carefully. You can edit cells "
        "before using these records for business questions."
    )

    extracted_df = pd.DataFrame(
        st.session_state.extracted_sales
    )

    expected_columns = [
        "date",
        "product",
        "quantity",
        "unit_price",
        "total_amount",
    ]

    for column in expected_columns:
        if column not in extracted_df.columns:
            extracted_df[column] = None

    extracted_df = extracted_df[expected_columns]

    reviewed_sales = st.data_editor(
        extracted_df,
        num_rows="dynamic",
        use_container_width=True,
        key="reviewed_sales_editor",
        column_config={
            "date": st.column_config.TextColumn("Date"),
            "product": st.column_config.TextColumn("Product"),
            "quantity": st.column_config.NumberColumn(
                "Quantity",
                min_value=0,
            ),
            "unit_price": st.column_config.NumberColumn(
                "Unit price (₦)",
                min_value=0,
            ),
            "total_amount": st.column_config.NumberColumn(
                "Total amount (₦)",
                min_value=0,
            ),
        },
    )

    st.caption(
        "If a figure is unclear, check your original sales book "
        "rather than guessing."
    )


# Prepare business information for Kasuwa's chat.
business_context = (
    f"The trader's available restocking budget is ₦{budget:,.2f}."
)

if sales_data is not None:
    business_context += (
        "\nUploaded spreadsheet columns: "
        + ", ".join(map(str, sales_data.columns))
        + "\nUploaded spreadsheet records:\n"
        + sales_data.head(100).to_csv(index=False)
    )

if reviewed_sales is not None and not reviewed_sales.empty:
    business_context += (
        "\nSales records extracted from photos and reviewed by "
        "the trader:\n"
        + reviewed_sales.to_csv(index=False)
    )


st.divider()
st.header("3. Ask Kasuwa AI")

question = st.text_area(
    "What would you like help with?",
    placeholder=(
        "Example: Based on my sales, which products should I "
        "consider restocking with my budget?"
    ),
)

if st.button("Ask Kasuwa AI", type="primary"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Kasuwa AI is thinking..."):
            answer = ask_gemma(question, business_context)

        st.markdown("### Kasuwa AI's Response")
        st.write(answer)

st.caption(
    "Kasuwa AI is under development. Verify extracted records "
    "and recommendations before making purchasing decisions."
)
