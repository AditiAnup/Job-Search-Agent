import streamlit as st

#Function for the side navigation bar
def Nav_bar():
    with st.sidebar:
        st.page_link('app.py', label='Job Search', icon='🔥')
        st.page_link('pages/Job_analysis.py', label='Job Analysis')
        st.page_link('pages/selected_job.py', label='Resume Optimization')