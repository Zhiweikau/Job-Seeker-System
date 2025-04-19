import streamlit as st
from streamlit_option_menu import option_menu

def navbar(current_page):
    selected = option_menu(
        menu_title=None,
        options=["Skill_Analyzed", "Visualization"],
        icons=["app", "bar-chart-line-fill"],
        menu_icon="cast",
        default_index=0 if current_page == "Skill_Analyzed" else 1,
        orientation="horizontal",
        styles={
            "container": {"padding": "1px", "background-color": "#1e1e1e", "border-radius": "20px", "width": "30%", "margin":"0",},
            "icon": {"color": "black", "font-size": "12px"}, 
            "nav-link": {
                "background-color": "#f0f0f5",  
                "border-radius": "15px",
                "padding": "5px 8px",
                "font-size": "10px",
                "color": "#333",
            },
            "nav-link-selected": {
                "background-color": "#3e8e41", 
                "color": "white",
                "font-weight": "bold",
            },
        },
    )

    if selected != current_page:
        st.switch_page(f"Pages/{selected}.py")