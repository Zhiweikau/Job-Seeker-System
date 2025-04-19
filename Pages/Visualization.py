import streamlit as st
import plotly.express as px
from Navigation import navbar
from Helper.Function import load_job_embeddings

st.set_page_config(layout="wide")

navbar("Visualization")

st.title("Job Market Trend and Analysis")

if st.button('Reset', key="reset", help="Clear all session states and go back to page Job_Search"):
    st.session_state.clear()
    st.switch_page("./Pages/Job_Search.py")
    st.rerun()

if 'selected_position' in st.session_state and st.session_state.selected_position:
    position_selected = st.session_state.selected_position

if (
    'selected_position' not in st.session_state or
    st.session_state.selected_position is None
):
    error_message = """
    <div style="color: red; font-size: 32px; font-weight: bold; text-align: center;">
        Please apply the Job after upload your Resume.
    </div>
    """
    st.markdown(error_message, unsafe_allow_html=True)
    st.stop()

df_updated_j = load_job_embeddings()
filtered_df = df_updated_j[df_updated_j['Position'] == position_selected]

col1, space1, col2, space2, col3 = st.columns([1, 0.1, 1, 0.1, 1])

def plot_pie_and_bar(column_name1, column_name2, col):
    with col:
        with st.container():
            # Pie Chart for column_name1
            dist = filtered_df[column_name1].value_counts().reset_index()
            dist.columns = [column_name1, 'Count']
            pie_fig = px.pie(dist, names=column_name1, values='Count', 
                             title=f"Distribution of {column_name1}s for {position_selected}",
                             color=column_name1, hole=0.3, color_discrete_sequence=px.colors.sequential.RdBu,)

            pie_fig.update_layout(
                title_font=dict(size=16, family='Arial, sans-serif', color='white'),
                font=dict(family='Arial, sans-serif', size=14, color='white'),
            )
            st.plotly_chart(pie_fig, use_container_width=True)

        with st.container():
            # Bar Chart for column_name2 (Average Salary by column_name2)
            avg_salary_by_column = filtered_df.groupby(column_name2)['Salary'].mean().reset_index()

            bar_fig = px.bar(avg_salary_by_column, x=column_name2, y='Salary', 
                             title=f"Average Salary for Each {column_name2} in {position_selected}",
                             labels={column_name2: column_name2, 'Salary': 'Average Salary'},
                             template="plotly_dark", color=column_name2)

            bar_fig.update_layout(
                title_font=dict(size=16, family='Arial, sans-serif', color='white'),
                font=dict(family='Arial, sans-serif', size=14, color='white'),
                xaxis_title=column_name2,  
                yaxis_title="Average Salary"
            )

            st.plotly_chart(bar_fig, use_container_width=True)

plot_pie_and_bar('Job Type', 'Field', col1)
plot_pie_and_bar('State', 'State', col2)
plot_pie_and_bar('Level', 'Level', col3)