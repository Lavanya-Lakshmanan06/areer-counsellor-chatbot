import streamlit as st
import csv
from datetime import datetime
from fpdf import FPDF

# Page config
st.set_page_config(page_title="AI Career Counsellor", page_icon="🎓", layout="wide")

# CSS Styling
st.markdown("""
<style>
body {
    background: linear-gradient(-45deg, #e3f2fd, #e1bee7, #ffe0b2, #c8e6c9);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
h2 { color: #4a148c; text-align: center; animation: glow 1.5s ease-in-out infinite alternate; }
@keyframes glow {
  from { text-shadow: 0 0 10px #ba68c8, 0 0 20px #ba68c8; }
  to { text-shadow: 0 0 20px #ff4081, 0 0 30px #ff4081; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2>✨ AI Virtual Career Counsellor (Chat Version) ✨</h2>", unsafe_allow_html=True)

# Initialize session state for chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = False
    st.session_state.quiz_qn = 0
    st.session_state.quiz_answers = []
if "matched_categories" not in st.session_state:
    st.session_state.matched_categories = []

# Quiz setup
quiz_questions = [
    "1️⃣ What activity do you enjoy most? (e.g., tech, design, farming)",
    "2️⃣ Which trait describes you best? (e.g., creativity, leadership, empathy)",
    "3️⃣ What excites you the most? (e.g., AI, fashion, plants, education)"
]

# Data maps
career_icons = {
    "Web Developer": "💻", "AI Engineer": "🧠", "Graphic Designer": "🎨", "Organic Farmer": "🌾",
    "Nurse": "🩺", "UI/UX Designer": "📱", "Animator": "🎞️", "Video Editor": "✂️",
    "Digital Marketer": "📢", "Entrepreneur": "🚀", "School Teacher": "👩‍🏫", "Accountant": "📊"
}

career_map = {
    "tech": ["Web Developer", "AI Engineer", "IT Support", "Data Analyst"],
    "design": ["Graphic Designer", "UI/UX Designer", "Animator", "Video Editor", "Fashion Stylist"],
    "farming": ["Organic Farmer", "Agri-Tech Entrepreneur", "Food Processing Expert"],
    "business": ["Digital Marketer", "Retail Manager", "Sales Executive", "Entrepreneur"],
    "health": ["Nurse", "Pharma Sales Rep", "Community Health Worker", "Lab Technician"],
    "education": ["School Teacher", "Online Tutor", "EdTech Content Creator"],
    "finance": ["Accountant", "Loan Officer", "Microfinance Assistant"]
}

category_keywords = {
    "tech": ["tech", "technology", "computers", "coding", "software"],
    "design": ["design", "fashion", "styling", "dress", "drawing", "illustration", "editing", "art", "creative"],
    "farming": ["farming", "agriculture", "farmer", "organic", "soil", "crops"],
    "business": ["business", "marketing", "sales", "startup", "entrepreneur"],
    "health": ["health", "nurse", "pharma", "medical", "clinic"],
    "education": ["teaching", "teacher", "education", "tutor", "learning"],
    "finance": ["finance", "accounting", "money", "banking", "loans"]
}

scheme_map = {
    "tech": ["Skill India: https://skillindia.gov.in", "NCS Portal: https://ncs.gov.in"],
    "design": ["Mudra Loan: https://mudra.org.in", "Udyam Registration: https://udyamregistration.gov.in"],
    "farming": ["PMEGP Agro: https://kviconline.gov.in", "Agri Machinery: https://agrimachinery.nic.in"],
    "business": ["Startup India: https://startupindia.gov.in", "NSIC MSME: https://nsic.co.in"],
    "health": ["NHM: https://nhm.gov.in", "Skill India Healthcare: https://skillindia.gov.in"],
    "education": ["NPTEL: https://nptel.ac.in", "Digital India: https://digitalindia.gov.in"],
    "finance": ["Mudra Loan: https://mudra.org.in", "Stand Up India: https://standupmitra.in"]
}

state_schemes = {
    "Tamil Nadu": ["MSME TN: https://msmetamilnadu.tn.gov.in", "NEEDS Scheme"],
    "Maharashtra": ["Mahaparwan Yojana", "Cluster Dev Program"],
    "Karnataka": ["Udyami Helpline", "Elevate 100"],
    "Kerala": ["KSIDC YEP", "Kerala MSME"],
    "Other": ["Udyam Registration: https://udyamregistration.gov.in", "MSMEX: https://msmex.in"]
}

course_map = {
    "Web Developer": ["Skill India Web Dev", "Coursera Full Stack"],
    "AI Engineer": ["NPTEL AI", "YouTube AI"],
    "Graphic Designer": ["Canva School", "YouTube Design"],
    "Organic Farmer": ["AgriFarming.in", "YouTube Organic"],
    "Nurse": ["Skill India Nursing", "YouTube Nursing"]
}

skill_map = {
    "Web Developer": ["HTML", "CSS", "JavaScript", "Git"],
    "AI Engineer": ["Python", "ML", "DL", "Math"],
    "Graphic Designer": ["Photoshop", "Illustrator", "Canva"],
    "Organic Farmer": ["Soil Testing", "Composting", "Crop Rotation"],
    "Nurse": ["First Aid", "Patient Care", "Sanitation"]
}

# Helpers
def match_quiz(answers):
    score = {"tech": 0, "design": 0, "farming": 0, "business": 0, "health": 0, "education": 0}
    for ans in answers:
        a = ans.lower()
        if "tech" in a or "ai" in a or "computer" in a:
            score["tech"] += 1
        elif "design" in a or "fashion" in a or "style" in a:
            score["design"] += 1
        elif "farm" in a or "plant" in a or "nature" in a:
            score["farming"] += 1
        elif "business" in a or "sales" in a:
            score["business"] += 1
        elif "health" in a or "clinic" in a:
            score["health"] += 1
        elif "education" in a or "teach" in a or "school" in a:
            score["education"] += 1
    return max(score, key=score.get)

def generate_pdf(categories, state):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Career Report", ln=True, align="C")
    pdf.ln(10)
    for cat in categories:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, f"Category: {cat.title()}", ln=True)
        pdf.set_font("Arial", '', 11)
        for job in career_map[cat]:
            pdf.cell(200, 10, f"- {job}", ln=True)
            if job in skill_map:
                skills = ", ".join(skill_map[job])
                pdf.cell(200, 8, f"  Skills: {skills}", ln=True)
            if job in course_map:
                courses = ", ".join(course_map[job])
                pdf.cell(200, 8, f"  Courses: {courses}", ln=True)
        if cat in scheme_map:
            pdf.cell(200, 8, "  MSME Schemes:", ln=True)
            for s in scheme_map[cat]:
                pdf.cell(200, 8, f"   - {s}", ln=True)
        pdf.ln(5)
    if state:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, f"MSME Schemes in {state}:", ln=True)
        pdf.set_font("Arial", '', 11)
        for s in state_schemes[state]:
            pdf.cell(200, 8, f"- {s}", ln=True)
    path = "career_report.pdf"
    pdf.output(path)
    return path

def log_feedback(mode, categories, feedback):
    with open("feedback_log.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), mode, ", ".join(categories), feedback])

# --- Display chat history
for sender, msg in st.session_state.chat_history:
    with st.chat_message(sender):
        st.markdown(msg)

# --- Chat Input
user_input = st.chat_input("Type your interest or 'quiz' to begin")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    if st.session_state.quiz_mode:
        st.session_state.quiz_answers.append(user_input)
        st.session_state.quiz_qn += 1

        if st.session_state.quiz_qn < len(quiz_questions):
            q = quiz_questions[st.session_state.quiz_qn]
            st.session_state.chat_history.append(("assistant", q))
            with st.chat_message("assistant"):
                st.markdown(q)
        else:
            match = match_quiz(st.session_state.quiz_answers)
            st.session_state.matched_categories = [match]
            result_msg = f"🎯 Based on your quiz, you're matched to: **{match.title()}**"
            st.session_state.chat_history.append(("assistant", result_msg))
            with st.chat_message("assistant"):
                st.markdown(result_msg)
            st.session_state.quiz_mode = False
            st.session_state.quiz_qn = 0
            st.session_state.quiz_answers = []

    elif "quiz" in user_input.lower():
        st.session_state.quiz_mode = True
        st.session_state.quiz_qn = 0
        st.session_state.quiz_answers = []
        intro_q = quiz_questions[0]
        st.session_state.chat_history.append(("assistant", "🧠 Starting the quiz..."))
        st.session_state.chat_history.append(("assistant", intro_q))
        with st.chat_message("assistant"):
            st.markdown("🧠 Starting the quiz...")
            st.markdown(intro_q)
    else:
        matches = []
        for token in user_input.lower().split():
            for cat, keys in category_keywords.items():
                if token in keys and cat not in matches:
                    matches.append(cat)
        st.session_state.matched_categories = matches
        if matches:
            with st.chat_message("assistant"):
                st.markdown(f"🎯 Based on your input, we matched: **{', '.join(matches)}**")
        else:
            with st.chat_message("assistant"):
                st.markdown("❌ Couldn't match your interest. Try 'quiz' for better results.")

# --- Show matched career suggestions
if st.session_state.matched_categories:
    st.markdown("### 💼 Your Career Matches")
    for cat in st.session_state.matched_categories:
        st.markdown(f"#### {cat.title()}")
        for job in career_map[cat]:
            icon = career_icons.get(job, "💼")
            st.markdown(f"<div style='border:1px solid #ccc; padding:10px; border-radius:10px;'>"
                        f"<h4>{icon} {job}</h4>", unsafe_allow_html=True)
            if job in course_map:
                st.markdown("_🎓 Courses:_")
                for course in course_map[job]:
                    st.markdown(f"👉 {course}")
            if job in skill_map:
                st.markdown("_✅ Skills:_")
                for skill in skill_map[job]:
                    st.markdown(f"✅ {skill}")
            st.markdown("</div>", unsafe_allow_html=True)
        if cat in scheme_map:
            st.markdown("**📌 MSME Schemes:**")
            for scheme in scheme_map[cat]:
                st.markdown(f"- {scheme}")

    # --- Regional MSME
    st.markdown("### 🌍 Find MSME support in your state")
    state = st.selectbox("Select your State:", list(state_schemes.keys()))
    if state:
        st.info(f"📋 MSME Schemes for {state}:")
        for scheme in state_schemes[state]:
            st.markdown(f"🔗 {scheme}")

    # --- Download PDF
    if st.button("📄 Download Career Report"):
        path = generate_pdf(st.session_state.matched_categories, state)
        with open(path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="career_report.pdf")

    # --- Feedback
    st.markdown("#### 🙋 Feedback")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Yes"):
            st.success("Thanks! 😊")
            log_feedback("chat", st.session_state.matched_categories, "Yes")
    with col2:
        if st.button("👎 No"):
            st.warning("We’ll improve. 🙏")
            log_feedback("chat", st.session_state.matched_categories, "No")
