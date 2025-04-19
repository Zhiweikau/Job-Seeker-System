import streamlit as st

pages = {
    "MAIN APPLICATION":[
    st.Page('./Pages/Job_Search.py', title="Search For Job"),
    st.Page('./Pages/Skill_Analyzed.py', title="Skill Analysis"),
    st.Page('./Pages/Visualization.py', title="Visualization")
    ],
}

pg = st.navigation(pages)
pg.run()
