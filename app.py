import streamlit as st
import os
import tempfile

from utils import classify_resume


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Resume Classification",
    page_icon="📄",
    layout="wide"
)


# -----------------------------
# HEADER
# -----------------------------
st.title("📄 Resume Classification System")

st.markdown(
    """
    Upload a resume and let the machine learning model
    automatically classify it into the appropriate job role.
    """
)

st.divider()


# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload a resume",
    type=["pdf", "doc", "docx"],
    help="Upload a PDF, DOC, or DOCX resume."
)


# -----------------------------
# CLASSIFICATION
# -----------------------------
if uploaded_file is not None:

    st.success(f"Uploaded file: {uploaded_file.name}")

    if st.button("Classify Resume", type="primary"):

        temp_file_path = None

        try:

            # Create a temporary file preserving the extension
            suffix = os.path.splitext(uploaded_file.name)[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:

                temp_file.write(uploaded_file.getvalue())

                temp_file_path = temp_file.name

            # Classification
            with st.spinner("Extracting and analyzing resume..."):

                resume_text, predicted_role, result = classify_resume(
                    temp_file_path
                )

            # -----------------------------
            # PREDICTION RESULT
            # -----------------------------
            st.divider()

            st.subheader("Classification Result")

            st.success(f"Predicted Job Role: {predicted_role}")

            # -----------------------------
            # PROBABILITY TABLE
            # -----------------------------
            st.subheader("Job Role Probability Ranking")

            result_display = result.copy()

            result_display["Probability"] = (
                result_display["Probability"] * 100
            ).round(2)

            result_display = result_display.rename(
                columns={"Probability": "Probability (%)"}
            )

            st.dataframe(
                result_display,
                use_container_width=True,
                hide_index=True
            )

            # -----------------------------
            # VISUALIZATION
            # -----------------------------
            st.subheader("Probability Visualization")

            chart_data = result_display.set_index("Job Role")

            st.bar_chart(
                chart_data["Probability (%)"],
                horizontal=True
            )

            # -----------------------------
            # RESUME PREVIEW
            # -----------------------------
            st.subheader("Extracted Resume Text")

            with st.expander("View extracted resume content"):

                st.text_area(
                    "Resume Content",
                    value=resume_text,
                    height=400,
                    disabled=True
                )

        except Exception as e:

            st.error(f"An error occurred: {e}")

        finally:

            # Delete temporary file
            if temp_file_path and os.path.exists(temp_file_path):

                os.remove(temp_file_path)