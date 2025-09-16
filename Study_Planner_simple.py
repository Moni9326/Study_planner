import streamlit as st
import requests
from datetime import datetime

# Simple page config
st.set_page_config(page_title="Study Planner", page_icon="📚")

# Initialize session state
if 'study_plan' not in st.session_state:
    st.session_state.study_plan = ""
if 'courses' not in st.session_state:
    st.session_state.courses = []

st.title("📚 AI Study Planner")

# Course input
st.subheader("Add Course")
col1, col2 = st.columns(2)

with col1:
    course = st.text_input("Course Name", placeholder="e.g., Mathematics")
    deadline = st.date_input("Deadline")
with col2:
    assignment = st.text_input("Assignment", placeholder="e.g., Final Project")
    hours = st.number_input("Hours needed", min_value=1, value=5)

if st.button("Add") and course and assignment:
    st.session_state.courses.append({
        "course": course,
        "assignment": assignment,
        "deadline": deadline.strftime("%Y-%m-%d"),
        "hours": hours
    })
    st.rerun()

# Show courses
if st.session_state.courses:
    st.subheader("Your Courses")
    for c in st.session_state.courses:
        st.write(f"**{c['course']}**: {c['assignment']} - Due: {c['deadline']} ({c['hours']}h)")

# Study preferences
st.subheader("Study Preferences")
hours_per_day = st.slider("Hours per day", 1, 8, 4)
style = st.selectbox("Study style", ["Focused sessions", "Spaced repetition", "Mixed"])

def call_groq_api(prompt):
    """Simple Groq API call with hardcoded key"""
    api_key = "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"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "system", "content": "You are a study planner. Create clear, actionable study schedules."},
            {"role": "user", "content": prompt}
        ],
        "model": "llama-3.1-8b-instant",
        "temperature": 0.7,
        "max_tokens": 800
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Generate plan
if st.button("🚀 Generate Study Plan", type="primary"):
    if not st.session_state.courses:
        st.error("Please add at least one course")
    else:
        # Prepare prompt
        courses_text = ""
        for c in st.session_state.courses:
            courses_text += f"- {c['course']}: {c['assignment']} (Due: {c['deadline']}, {c['hours']} hours)\n"
        prompt = f"""Create a study plan for:
{courses_text}
Available time: {hours_per_day} hours/day
Style: {style}
Current date: {datetime.now().strftime("%Y-%m-%d")}
Provide a weekly schedule with daily tasks and time blocks."""
        with st.spinner("Generating plan..."):
            plan = call_groq_api(prompt)
            if plan:
                st.session_state.study_plan = plan

# Show plan
if st.session_state.study_plan:
    st.subheader("📅 Your Study Plan")
    st.markdown(st.session_state.study_plan)
    st.download_button("Download Plan", st.session_state.study_plan, "study_plan.txt")

# Simple clear button
if st.button("Clear All"):
    st.session_state.courses = []
    st.session_state.study_plan = ""
    st.rerun()
