import sys
sys.path.append(".")
import streamlit as st
import pandas as pd
import base64
import numpy as np
import io
from PyPDF2 import PdfReader
from sklearn.metrics.pairwise import cosine_similarity
from Helper.Function import load_embedding_model, load_job_embeddings, extract_skills_from_job_responsibility, extract_skills_from_resume

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
        }
        
        .stButton>button:first-child {
            background-color: #1abc9c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .stButton>button:first-child:hover {
            background-color: #16a085;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Job Seeker System")

# Ensure uploader key and resume state exist
if 'resume_pdf' not in st.session_state:
    st.session_state.resume_pdf = None
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

col1, spacer, col2 = st.columns([1, 0.1, 1])

with col1:
    st.markdown("### 📎 Upload Your Resume (PDF only)")

    uploaded_file = st.file_uploader(
        "Upload a file",
        type=["pdf"],
        key=st.session_state.uploader_key
    )
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
    if uploaded_file and uploaded_file.size > MAX_FILE_SIZE:
        st.error("File size exceeds the 10MB limit!")

    if uploaded_file is not None:
        base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
        st.session_state.resume_pdf = base64_pdf
        st.success("✅ PDF uploaded and stored in session for further analysis!")

    if st.session_state.resume_pdf is not None:
        st.markdown("#### 📄 Preview of Uploaded PDF")
        pdf_display = f"""
        <iframe src="data:application/pdf;base64,{st.session_state.resume_pdf}"
                width="100%" height="700" type="application/pdf"></iframe>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)

        if st.button("Clear Uploaded Resume"):
            st.session_state.resume_pdf = None
            st.session_state.uploader_key += 1 
            st.session_state.selected_job = None
            st.session_state.extracted_skills_df = None
            st.session_state.extracted_skills_from_job = None
            st.session_state.top30 = None
            st.rerun()
    else:
        st.info("Please upload a resume to begin.")

with col2:
    st.markdown("### 🔍 Matching Area")

    if st.session_state.resume_pdf is not None:
        with st.spinner("Embedding your resume and calculating matching scores..."):
            pdf_bytes = base64.b64decode(st.session_state.resume_pdf)
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))

            model = load_embedding_model()
            page_texts = [page.extract_text() for page in pdf_reader.pages if page.extract_text()]
            page_embeddings = model.encode(page_texts)
            resume_embedding = np.mean(page_embeddings, axis=0)

            df_updated_j = load_job_embeddings()
            job_embeddings = np.vstack(df_updated_j["Embeddings cleaned responsibilities"].values)

            # Compute similarity
            similarity_scores = cosine_similarity([resume_embedding], job_embeddings)[0]
            df_updated_j["Matching Score"] = similarity_scores
            df_updated_j = df_updated_j.sort_values(by="Matching Score", ascending=False)
            df_updated_j["Matching Score"] = (df_updated_j["Matching Score"] * 100).round(2).astype(str) + "%"

            st.session_state.matched_jobs = df_updated_j

            st.success("Matching Complete! Top job matches below:")

            if 'selected_job' in st.session_state and st.session_state.selected_job is not None:
                job = st.session_state.selected_job
                with st.container():
                    st.markdown("### Job Details")
                    
                    # Create a scrollable container with a fixed height for job details
                    job_details_html = f"""
                    <div style="max-height: 400px; overflow-y: auto; padding: 15px; border: 5px solid #ccc; border-radius: 25px; background-color: #333333;">
                        <strong>Job Title:</strong> {job['Job Title']}<br>
                        <div style="margin-bottom: 20px;"<strong>Company Name:</strong> {job['Company Name']}<br>
                        <div style="margin-bottom: 20px;"<strong>Location:</strong> {job['Location']}<br>
                        <div style="margin-bottom: 20px;"<strong>Sector:</strong> {job['Sector']}<br>
                        <div style="margin-bottom: 20px;"<strong>Job Type:</strong> {job['Job Type']}<br>
                        <div style="margin-bottom: 20px;"<strong>Salary:</strong> RM {job['Salary']}<br>
                        <div style="margin-bottom: 20px;"<strong>Job Responsibilities:</strong> {job['Job Responsibilities']}
                    </div>
                    """
                    
                    # Display the job details with the scrollable container
                    st.markdown(job_details_html, unsafe_allow_html=True)

                st.markdown("---")

            st.markdown("**Job Posts**")
            job_list = df_updated_j.head(10)
            for i, job in job_list.iterrows():
                # Create the job card HTML
                job_card = f"""
                <div style="display: flex; justify-content: space-between; border: 1px solid #ccc; padding: 5px; margin-bottom: 10px; border-radius: 15px; background-color: #333333; max-height: 150px;">
                    <div style="flex: 3;">
                        <strong style="color: #fff; font-size: 12px;">Job Title:</strong> <span style="color: #fff; font-size: 12px;">{job['Job Title']}</span><br>
                        <strong style="color: #fff; font-size: 12px;">Company Name:</strong> <span style="color: #fff; font-size: 12px;">{job['Company Name']}</span><br>
                        <strong style="color: #fff; font-size: 12px;">Salary:</strong> <span style="color: #fff; font-size: 12px;">RM {job['Salary']}</span><br>
                        <strong style="color: #fff; font-size: 14px;">Matching Score:</strong> <span style="color: #FF0000; font-size: 14px;">{job['Matching Score']}</span><br>
                    </div>
                    <div style="flex: 1; display: flex; align-items: center; justify-content: flex-end;">
                """

                # Display the job card HTML
                st.markdown(job_card, unsafe_allow_html=True)

                # Add 'View' and 'Apply' buttons below the job card
                col1, col2 = st.columns([1, 1])

                with col1:
                    if st.button("View", key=f"view_{i}"):
                        st.session_state.selected_job = job
                        st.rerun()

                with col2:
                    if st.button("Apply", key=f"apply_{i}"):
                        st.session_state.apply_job = job
                        if 'apply_job' in st.session_state and st.session_state.apply_job is not None:
                            job = st.session_state.apply_job
                        
                            pdf_data = base64.b64decode(st.session_state.resume_pdf)
                            pdf_reader = PdfReader(io.BytesIO(pdf_data))
                            resume_text = ''
                            for page in pdf_reader.pages:
                                resume_text += page.extract_text()
                            combined_skills = extract_skills_from_resume(resume_text)
                            skills_data = {"Extracted Skills": [combined_skills]}
                            skills_df = pd.DataFrame(skills_data)
                            st.session_state.extracted_skills_df = skills_df

                            extracted_skills_from_job = extract_skills_from_job_responsibility(job['Cleaned_Responsibilities'])
                            job['Extracted Skills'] = extracted_skills_from_job
                            st.session_state.extracted_skills_from_job = job
                            position_selected = job['Position']
                            st.session_state.selected_position = position_selected
                        st.switch_page("./Pages/Skill_Analyzed.py")
                        st.rerun()

    else:
        st.info("Resume not found. Please upload a resume to start matching.")