import sys
sys.path.append(".")
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Helper.Function import get_top_matches
from Navigation import navbar

st.set_page_config(layout="wide")

navbar("Skill_Analyzed")

st.title("📊 Skill Analyzed and 💻 Course Recommendation")

if st.button("Back"):
    st.switch_page("./Pages/Job_Search.py")

if (
    'extracted_skills_from_job' not in st.session_state or
    st.session_state.extracted_skills_from_job is None or
    'extracted_skills_df' not in st.session_state or
    st.session_state.extracted_skills_df is None
):
    error_message = """
    <div style="color: red; font-size: 32px; font-weight: bold; text-align: center;">
        Please apply the Job after upload your Resume.
    </div>
    """
    st.markdown(error_message, unsafe_allow_html=True)
    st.stop()

if 'top_30' not in st.session_state:
    st.session_state.top_30 = None

def update_page(delta):
    st.session_state.current_page += delta
    st.session_state.page = st.session_state.current_page

if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
    
targeted_skills = st.session_state.extracted_skills_from_job['Extracted Skills']
current_skills = st.session_state.extracted_skills_df['Extracted Skills'].iloc[0]


targeted_clean = [skill.strip().lower() for skill in targeted_skills]
current_clean = [skill.strip().lower() for skill in current_skills]

exact_matches = [skill for skill in targeted_clean if skill in current_clean]
top_targeted_skills = exact_matches[:6]
top_current_skills = exact_matches[:6]

if len(top_targeted_skills) < 6:
    remaining_targeted = [skill for skill in targeted_clean if skill not in exact_matches]
    remaining_current = [skill for skill in current_clean if skill not in exact_matches]

    similar_targeted = get_top_matches(remaining_targeted, remaining_current, 6 - len(top_targeted_skills))
    similar_current = get_top_matches(remaining_current, remaining_targeted, 6 - len(top_current_skills))

    # Combine exact matches with the new similar ones, ensuring no duplicates
    for skill in similar_targeted:
        if skill not in top_targeted_skills:
            top_targeted_skills.append(skill)

    for skill in similar_current:
        if skill not in top_current_skills:
            top_current_skills.append(skill)

    top_targeted_skills = top_targeted_skills[:6]
    top_current_skills = top_current_skills[:6]

vectorizer = TfidfVectorizer().fit(top_targeted_skills + top_current_skills)  
targeted_vecs = vectorizer.transform(top_targeted_skills)  
current_vecs = vectorizer.transform(top_current_skills) 

similarity = cosine_similarity(targeted_vecs, current_vecs)

similarity_scores = similarity.diagonal()  # Diagonal elements give one-to-one comparison

top_targeted_skills_upper = [skill.title() for skill in top_current_skills]
data = {
    'Targeted Skills': top_targeted_skills_upper,
    'Matching Score': similarity_scores
}

df = pd.DataFrame(data)
fig = px.bar(df, 
             x='Matching Score', 
             y='Targeted Skills', 
             orientation='h',
             color='Matching Score', 
             color_continuous_scale='Blues',  
             title='Matching Score between Targeted and Current Skills',
             labels={'Matching Score': 'Matching Score', 'Targeted Skills': 'Skills'},
             hover_data={'Targeted Skills': True, 'Matching Score': True}) 

fig.update_layout(
    title_x=0,  
    title_font_size=16,  
    xaxis_title_font_size=14,
    yaxis_title_font_size=14,
    showlegend=False 
)

remaining_missing = [skill for skill in targeted_clean if skill not in current_clean]
top_missing_skills = get_top_matches(remaining_missing, current_clean, 5)

# Display in HTML format
def list_to_html(title, skill_list):
    html = f"<h5>{title}</h5><ul>"
    for skill in skill_list:
        html += f"<li>{skill.title()}</li>"
    html += "</ul>"
    return html

missing_html = list_to_html("❌ Missing Skills", top_missing_skills)

col1, space, col2 = st.columns([0.7, 0.1, 1.2])

with col1:
    st.plotly_chart(fig)
    st.markdown(missing_html, unsafe_allow_html=True)

with col2:
    if st.button("Course Recommendation"):
        try:
            if st.session_state.top_30 is None:
                df_c =  pd.read_pickle("./Dataset/Coursera/Coursera_after_embeddings.pkl")
                model = SentenceTransformer('all-MiniLM-L6-v2')
                missing_skills_embeddings = model.encode(" ".join(top_missing_skills))
                embeddings_skills = df_c['Embeddings skills'].apply(np.array)
                embeddings_skills = np.vstack(df_c['Embeddings skills'].values)

                similarity_scores_course = cosine_similarity([missing_skills_embeddings], embeddings_skills)[0]
                df_c["Similarity"] = similarity_scores_course
                df_c = df_c.sort_values(by="Similarity", ascending=False)

                top30_courses = df_c.head(30)
                st.session_state.top_30 = top30_courses
           
        except FileNotFoundError:
            st.error("Pickle file not found!")


    if st.session_state.top_30 is not None:
        top30_courses = st.session_state.top_30
        items_per_page = 9
        total_pages = len(top30_courses) // items_per_page + (1 if len(top30_courses) % items_per_page > 0 else 0)
        start_index = st.session_state.current_page * items_per_page
        end_index = start_index + items_per_page

        st.subheader("Recommended Training Programs and Certificates")

        with st.container():
            cols = st.columns(3)

            for i in range(start_index, end_index):
                if i >= len(top30_courses):
                    break
                course = top30_courses.iloc[i]

                with cols[i % 3]:
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="
                                border: 3px solid #FF4B4B;
                                padding: 5px;
                                border-radius: 15px;
                                background-color: #1E1E1E;
                                color: white;
                                text-align: center;
                                height: 400px;
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                            ">
                                <img src="{course['Course Image']}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 10px; margin-top: 8px;" alt="Course Image">
                                <img src="{course['Provider Image']}" style="width: 30px; height: 30px; border-radius: 20%; margin-top: 10px;" alt="Provider Image">
                                <h4 style="margin: 1px 0; font-size: 14px;">{course['Course Name']}</h4>
                                <p style="font-size: 11px;"><b>Skills Included:</b> {course['Skills Gained']}</p>
                                <p style="font-size: 11px;"><b>Rating Score:</b> {course['Rating Score']}</p>
                                <p style="font-size: 11px;"><b>Level & Duration:</b> {course['Level & Duration']}</p>
                            </div>
                            """, unsafe_allow_html=True
                        )

                        st.markdown(
                            f"""
                            <style>
                                .enroll-button {{
                                    background-color: #008080;
                                    color: white;
                                    padding: 3px 3px;
                                    border: none;
                                    border-radius: 25px;
                                    cursor: pointer;
                                    width: 100%;
                                    font-size: 15px;
                                    text-align: center;
                                }}
                            </style>
                            """, unsafe_allow_html=True)

                        st.markdown(
                            f'<a href="{course["Course Link"]}" target="_blank"><button class="enroll-button">Enroll</button></a>',
                            unsafe_allow_html=True
                        )

            col_left, col_middle, col_right = st.columns([1.8, 7, 1.5])
            with col_left:
                st.button("⬅ Previous", disabled=(start_index == 0), on_click=lambda: update_page(-1))

            with col_middle:
                st.empty()

            with col_right:
                st.button("Next ➡", disabled=(end_index >= len(top30_courses)), on_click=lambda: update_page(1))
    else:
        st.markdown("Please click the 'Course Recommendation' button to proceed the recommended courses.")