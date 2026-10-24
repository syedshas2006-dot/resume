"""
AI Resume Analyzer & Job Recommendation System
==============================================
Main Streamlit Application
A modern, responsive, beginner-friendly web application for parsing resumes,
matching candidate competencies against data/AI job roles using TF-IDF and
Cosine Similarity, and generating actionable 4-week learning roadmaps.
"""

import os
import sys
import tempfile
import io
import pandas as pd
import streamlit as st

# Configure matplotlib temporary cache directory to prevent permission warnings
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib_cache")

# Add application directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from text_cleaner import clean_text, extract_sections
from resume_parser import parse_resume
from skill_extractor import SkillExtractor
from job_matcher import JobMatcher, DISCLAIMER_TEXT
from roadmap_generator import generate_roadmap

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer & Job Matcher",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Professional Navy & Clean Blue Theme)
st.markdown(
    """
    <style>
    /* Global Styles */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 2px 4px 4px 0;
    }
    .badge-matched {
        background-color: #DCFCE7;
        color: #166534;
        border: 1px solid #86EFAC;
    }
    .badge-missing {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FCA5A5;
    }
    .badge-category {
        background-color: #EFF6FF;
        color: #1E40AF;
        border: 1px solid #BFDBFE;
    }
    .card-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .highlight-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        color: white !important;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 18px;
    }
    .highlight-card h3, .highlight-card p, .highlight-card span {
        color: white !important;
    }
    .disclaimer-box {
        background-color: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 0.88rem;
        color: #92400E;
        margin-top: 15px;
    }
    .privacy-box {
        background-color: #F0FDF4;
        border-left: 4px solid #22C55E;
        padding: 10px 14px;
        border-radius: 4px;
        font-size: 0.83rem;
        color: #166534;
        margin-bottom: 15px;
    }
    .tanglish-banner {
        background-color: #F8FAFC;
        border: 1px dashed #94A3B8;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_system_engines():
    """Initializes and caches the skill extractor and job matcher."""
    extractor = SkillExtractor()
    matcher = JobMatcher()
    return extractor, matcher


skill_extractor, job_matcher = load_system_engines()


def generate_download_report(
    resume_meta: dict,
    detected_skills: list,
    match_results: dict,
    target_role_info: dict,
    roadmap_info: dict,
) -> str:
    """Creates a comprehensive text analysis report for download."""
    lines = [
        "=" * 70,
        "AI RESUME ANALYZER & JOB RECOMMENDATION REPORT",
        "=" * 70,
        f"File Analyzed        : {resume_meta.get('file_name', 'Uploaded Resume')}",
        f"File Type            : {resume_meta.get('file_type', 'N/A')}",
        f"Word Count           : {resume_meta.get('word_count', 0)} words",
        f"Skills Identified    : {len(detected_skills)} skills",
        "-" * 70,
        "\n1. EXTRACTED TECHNICAL SKILLS:",
        ", ".join(detected_skills) if detected_skills else "None detected",
        "\n" + "-" * 70,
        "2. ESTIMATED JOB ROLE MATCH RANKINGS:",
    ]

    for idx, role in enumerate(match_results.get("all_roles", []), 1):
        lines.append(
            f"   #{idx} {role['role_title']:<26} | Match Score: {role['estimated_match_score']}% "
            f"(Skills Overlap: {role['skill_match_percentage']}%, TF-IDF: {role['tfidf_similarity_percentage']}%)"
        )

    lines.extend([
        "\n" + "-" * 70,
        f"3. TARGET ROLE DEEP DIVE: {target_role_info['role_title'].upper()}",
        f"Estimated Match Score: {target_role_info['estimated_match_score']}%",
        f"Matched Skills ({len(target_role_info['matched_skills'])}): "
        + (", ".join(target_role_info["matched_skills"]) if target_role_info["matched_skills"] else "None"),
        f"Missing Skills ({len(target_role_info['missing_skills'])}): "
        + (", ".join(target_role_info["missing_skills"]) if target_role_info["missing_skills"] else "None"),
        "\n" + "-" * 70,
        f"4. 4-WEEK LEARNING ROADMAP ({roadmap_info['target_role']}):",
    ])

    for week in roadmap_info.get("weeks", []):
        lines.append(f"\n[{week['title'].upper()}]")
        lines.append(f"Goal       : {week['goal']}")
        lines.append(f"Deliverable: {week['deliverable']}")
        lines.append("Tasks      :")
        for t in week.get("tasks", []):
            lines.append(f"  * {t['title']}: {t['action']} (Resource: {t['resource']})")

    lines.extend([
        "\n" + "=" * 70,
        "DISCLAIMER:",
        DISCLAIMER_TEXT,
        "=" * 70,
    ])
    return "\n".join(lines)


# ==========================================
# SIDEBAR: UPLOAD & CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("### 📄 Resume Ingestion")
    
    st.markdown(
        """
        <div class="privacy-box">
            🔒 <b>Privacy First:</b> Resumes are processed in-memory. No permanent storage or personal logs.
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload Resume (PDF or DOCX)",
        type=["pdf", "docx"],
        help="Upload standard text-based PDF or Word documents up to 5MB.",
    )

    st.markdown("---")
    st.markdown("#### 🧪 Or Try Sample Resumes")
    sample_choice = st.selectbox(
        "Load sample profile to test immediately:",
        [
            "Select a sample...",
            "Data Analyst Profile (DOCX)",
            "Machine Learning Engineer Profile (DOCX)",
            "NLP & AI Engineer Profile (DOCX)",
            "Computer Vision Profile (DOCX)",
            "Empty / Scanned PDF (Test Error Handling)",
        ],
    )

    st.markdown("---")
    st.markdown(
        """
        **System Architecture:**
        - **Parser:** `pypdf` & `python-docx`
        - **NLP Cleaner:** Regex + Token Masking
        - **Skill Matching:** 90+ Skill Taxonomy
        - **Similarity Engine:** TF-IDF & Cosine Similarity
        - **Roadmap:** Personalized 4-Week Plan
        """
    )


# Handle sample loading
file_name = None
file_bytes = None

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_bytes = uploaded_file.getvalue()
elif sample_choice != "Select a sample...":
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_resumes")
    sample_map = {
        "Data Analyst Profile (DOCX)": "sample_data_analyst.docx",
        "Machine Learning Engineer Profile (DOCX)": "sample_ml_engineer.docx",
        "NLP & AI Engineer Profile (DOCX)": "sample_nlp_engineer.docx",
        "Computer Vision Profile (DOCX)": "sample_cv_engineer.docx",
        "Empty / Scanned PDF (Test Error Handling)": "sample_empty_scanned.pdf",
    }
    actual_file = sample_map.get(sample_choice)
    if actual_file:
        sample_path = os.path.join(sample_dir, actual_file)
        if os.path.exists(sample_path):
            file_name = actual_file
            with open(sample_path, "rb") as f:
                file_bytes = f.read()


# ==========================================
# MAIN DASHBOARD INTERFACE
# ==========================================
st.markdown('<div class="main-title">AI Resume Analyzer & Job Matcher</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Intelligent resume parsing, keyword skill extraction, and TF-IDF career matching dashboard.</div>',
    unsafe_allow_html=True,
)

# Tanglish Quick Explainer Expander
with st.expander("💡 Enna Nadakkuthu? / How this AI Works (Tanglish Guide for Beginners)", expanded=False):
    st.markdown(
        """
        <div class="tanglish-banner">
            <h4>Vanakkam! 👋 Inga enna process nadakuthu-nu simple-aa paarkalam:</h4>
            <ul>
                <li><b>Step 1: Text Extraction & Cleaning</b> - Unga resume PDF/DOCX-la irunthu text extract pannuvom. Unwanted phone numbers, emails, bullet symbols lam clean aagum. Aana <code>C++</code>, <code>C#</code>, <code>.NET</code>, <code>SQL</code> maathiri technical terms mathiri safe-aa protect pannuvom!</li>
                <li><b>Step 2: Fair Evaluation (No Bias)</b> - Unga age, gender, photo, religion ethuvume scoring-la use aagathu. Strictly unga technical skills mattum thaane match aagum.</li>
                <li><b>Step 3: Skill Detection</b> - 90+ skills taxonomy vachi resume-la irukura skills identify panni, categories (Languages, ML, BI, Cloud) maathiri divide pannuvom.</li>
                <li><b>Step 4: TF-IDF & Cosine Similarity</b> - scikit-learn TF-IDF algorithm unga resume words and skills-ai mathematical vectors-aa maathi, 5 job roles kooda compare panni <b>Estimated Match Score</b> calculate pannum.</li>
                <li><b>Step 5: 4-Week Roadmap</b> - Target job-ku missing-aa irukura skills-ai 4 weeks-la learn panna beginner-friendly tasks & free resources ready pannum!</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

if not file_bytes:
    # Welcome & Empty State Screen
    st.info("👈 Please upload a PDF or DOCX resume from the sidebar, or select a preloaded sample resume to begin.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="card-box">
                <h4>1. Ingestion & Privacy</h4>
                <p style="color:#64748B; font-size:0.9rem;">
                    Upload PDF or DOCX. In-memory processing guarantees zero data leakage or persistent logging.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="card-box">
                <h4>2. TF-IDF Job Matching</h4>
                <p style="color:#64748B; font-size:0.9rem;">
                    Computes cosine similarity against Data Analyst, ML, AI, NLP, and Computer Vision profiles.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="card-box">
                <h4>3. 4-Week Skill Roadmap</h4>
                <p style="color:#64748B; font-size:0.9rem;">
                    Identifies missing competencies and drafts a step-by-step milestone plan with free learning resources.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.stop()


# ==========================================
# RESUME PARSING & PROCESSING PIPELINE
# ==========================================
with st.spinner("Analyzing resume content and matching technical competencies..."):
    # Step 1: Ingestion
    parse_result = parse_resume(file_name, file_bytes)

    if parse_result["status"] == "error":
        st.error(f"❌ **Parsing Error:** {parse_result['error_message']}")
        if parse_result.get("is_scanned"):
            st.warning(
                "💡 **Tip for Scanned Documents:** Scanned image PDFs cannot be read by text parsers. "
                "Please save your resume directly from Microsoft Word, Google Docs, or Canva as a text PDF or .docx file."
            )
        st.stop()

    raw_text = parse_result["raw_text"]

    # Step 2: Cleaning & Normalization (Preserving C++, C#, .NET, SQL)
    cleaned_text = clean_text(raw_text)

    # Step 3: Skill Extraction & Categorization
    skill_result = skill_extractor.extract_skills(cleaned_text)
    detected_skills = skill_result["detected_skills"]
    skills_by_category = skill_result["skills_by_category"]

    # Step 4: Job Matching & TF-IDF Scoring
    match_result = job_matcher.match_resume(cleaned_text, detected_skills)
    top_3 = match_result["top_3_recommendations"]
    best_role = match_result["best_match_role"]


# ==========================================
# TOP KPI METRIC CARDS
# ==========================================
st.markdown("### 📌 Executive Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Document", parse_result["file_name"][:18] + "...", f"{parse_result['file_size_kb']} KB")
with kpi2:
    st.metric("Total Word Count", f"{parse_result['word_count']} words", f"{parse_result['page_count']} page(s)")
with kpi3:
    st.metric("Identified Skills", f"{len(detected_skills)} skills", f"{len(skills_by_category)} categories")
with kpi4:
    best_score_label = f"{best_role['estimated_match_score']}%" if best_role else "0%"
    st.metric("Top Recommended Role", best_role["role_title"] if best_role else "N/A", best_score_label)

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# MAIN TABS
# ==========================================
tab_overview, tab_deepdive, tab_roadmap, tab_skills, tab_export = st.tabs([
    "📊 Job Recommendations",
    "🎯 Target Role Deep Dive",
    "🗓️ 4-Week Learning Roadmap",
    "🔍 Extracted Skills & Resume",
    "📥 Download Analysis Report",
])


# ----------------------------------------------------
# TAB 1: JOB RECOMMENDATIONS & RANKINGS
# ----------------------------------------------------
with tab_overview:
    st.markdown("### 🏆 Top Recommended Job Roles")
    st.caption("Ranked using a hybrid of keyword skill overlap (55%) and TF-IDF Cosine Similarity (45%).")

    rec_cols = st.columns(3)
    for idx, (col, role) in enumerate(zip(rec_cols, top_3), 1):
        with col:
            st.markdown(
                f"""
                <div class="card-box" style="border-top: 4px solid #2563EB;">
                    <span style="font-size:0.8rem; font-weight:700; color:#2563EB;">RANK #{idx}</span>
                    <h3 style="margin: 4px 0 10px 0; color:#0F172A;">{role['role_title']}</h3>
                    <p style="font-size:0.85rem; color:#64748B; min-height: 48px;">{role['overview']}</p>
                    <div style="margin: 12px 0;">
                        <span style="font-size:1.8rem; font-weight:800; color:#1E3A8A;">{role['estimated_match_score']}%</span>
                        <span style="font-size:0.85rem; color:#64748B;"> Estimated Match</span>
                    </div>
                    <div style="font-size:0.85rem; margin-bottom: 8px;">
                        <b>Skills Matched:</b> {role['matched_count']} / {role['total_required_count']}
                    </div>
                    <div style="font-size:0.82rem; color:#475569;">
                        <b>Experience Level:</b> {role['experience_level']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("### 📈 All Job Roles Comparison")

    # Prepare DataFrame for chart and table
    chart_data = []
    for r in match_result["all_roles"]:
        chart_data.append({
            "Job Role": r["role_title"],
            "Estimated Match Score (%)": r["estimated_match_score"],
            "Skill Overlap (%)": r["skill_match_percentage"],
            "TF-IDF Context Similarity (%)": r["tfidf_similarity_percentage"],
            "Skills Matched": f"{r['matched_count']}/{r['total_required_count']}",
        })
    df_roles = pd.DataFrame(chart_data)

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.bar_chart(
            df_roles.set_index("Job Role")[["Estimated Match Score (%)", "Skill Overlap (%)"]],
            color=["#2563EB", "#60A5FA"],
            height=320,
        )
    with c2:
        st.dataframe(
            df_roles[["Job Role", "Estimated Match Score (%)", "Skills Matched"]],
            hide_index=True,
            use_container_width=True,
        )

    st.markdown(
        f"""
        <div class="disclaimer-box">
            ⚠️ <b>Important Legal & Ethical Notice:</b> {DISCLAIMER_TEXT}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------
# TAB 2: TARGET ROLE DEEP DIVE & SKILL GAP ANALYSIS
# ----------------------------------------------------
with tab_deepdive:
    st.markdown("### 🎯 In-Depth Skill Gap Analysis")
    st.write("Select any target role to examine matched competencies vs. missing requirements.")

    all_titles = [r["role_title"] for r in match_result["all_roles"]]
    default_index = 0
    selected_title = st.selectbox("Choose Target Job Role:", all_titles, index=default_index)

    target_role = job_matcher.get_role_deep_dive(match_result, selected_title)

    if target_role:
        gap_col1, gap_col2, gap_col3 = st.columns(3)
        with gap_col1:
            st.metric("Estimated Match Score", f"{target_role['estimated_match_score']}%")
        with gap_col2:
            st.metric("Matched Skills", f"{len(target_role['matched_skills'])} / {target_role['total_required_count']}")
        with gap_col3:
            missing_count = len(target_role["missing_skills"])
            st.metric("Skills to Acquire (Gap)", f"{missing_count} skill(s)")

        # Progress bar
        score_val = target_role["estimated_match_score"] / 100.0
        st.progress(score_val, text=f"Overall Target Role Readiness: {target_role['estimated_match_score']}%")

        col_matched, col_missing = st.columns(2)

        with col_matched:
            st.markdown(
                f"""
                <div class="card-box" style="border-left: 5px solid #22C55E;">
                    <h4 style="color:#166534; margin-top:0;">✅ Matched Skills Detected ({len(target_role['matched_skills'])})</h4>
                    <p style="font-size:0.85rem; color:#64748B;">Competencies identified in both your resume and job requirements:</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if target_role["matched_skills"]:
                badges = "".join([f'<span class="badge-pill badge-matched">{s}</span>' for s in target_role["matched_skills"]])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.info("No matching skills detected for this profile yet.")

        with col_missing:
            st.markdown(
                f"""
                <div class="card-box" style="border-left: 5px solid #EF4444;">
                    <h4 style="color:#991B1B; margin-top:0;">⚠️ Skills Not Detected ({len(target_role['missing_skills'])})</h4>
                    <p style="font-size:0.85rem; color:#64748B;">Required competencies not found in your uploaded resume:</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if target_role["missing_skills"]:
                badges = "".join([f'<span class="badge-pill badge-missing">{s}</span>' for s in target_role["missing_skills"]])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.success("🎉 Outstanding! You have matched all essential skills for this job role!")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📋 Role Description & Responsibilities")
        # Find matching row description
        desc = ""
        for _, r in job_matcher.roles_df.iterrows():
            if r["role_title"] == selected_title:
                desc = r["description"]
                break
        st.info(desc)


# ----------------------------------------------------
# TAB 3: 4-WEEK LEARNING ROADMAP
# ----------------------------------------------------
with tab_roadmap:
    if target_role:
        roadmap = generate_roadmap(
            target_role=target_role["role_title"],
            missing_skills=target_role["missing_skills"],
            matched_skills=target_role["matched_skills"],
        )

        st.markdown(f"### 🗓️ 4-Week Learning Roadmap: {roadmap['target_role']}")
        st.write(roadmap["summary"])

        if roadmap["is_mastery_mode"]:
            st.success("🏆 **Mastery Mode Activated:** All baseline skills are present. This roadmap focuses on production scaling and architecture.")

        for week in roadmap["weeks"]:
            with st.expander(f"📌 {week['title']} (Focus: {', '.join(week['focus_skills']) if week['focus_skills'] else 'Mastery'})", expanded=True):
                st.markdown(f"**🎯 Weekly Goal:** {week['goal']}")
                st.markdown(f"**📦 Concrete Deliverable:** `{week['deliverable']}`")
                st.markdown("---")
                st.markdown("#### 📝 Action Items & Learning Resources:")

                for t_idx, task in enumerate(week["tasks"], 1):
                    col_chk, col_content = st.columns([0.05, 0.95])
                    with col_chk:
                        st.checkbox("", key=f"chk_{target_role['role_id']}_{week['week_number']}_{t_idx}")
                    with col_content:
                        st.markdown(f"**{task['title']}**")
                        st.markdown(f"• *Core Concept:* {task['concept']}")
                        st.markdown(f"• *Practical Task:* {task['action']}")
                        st.markdown(f"• *Recommended Resource:* [{task['resource']}](#)")
                        st.markdown("")


# ----------------------------------------------------
# TAB 4: EXTRACTED SKILLS & RESUME VIEWER
# ----------------------------------------------------
with tab_skills:
    st.markdown("### 🔍 Extracted Competencies by Category")
    st.caption(f"Identified {len(detected_skills)} unique skills across {len(skills_by_category)} taxonomy categories.")

    cat_cols = st.columns(2)
    for idx, (category, skills) in enumerate(skills_by_category.items()):
        col = cat_cols[idx % 2]
        with col:
            st.markdown(
                f"""
                <div class="card-box">
                    <h4 style="margin-top:0; color:#1E40AF;">{category} ({len(skills)})</h4>
                    <div>
                        {''.join([f'<span class="badge-pill badge-category">{s}</span>' for s in skills])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("### 📜 Cleaned Resume Text Viewer")
    with st.expander("View Normalized Text (Pre-scoring preview)", expanded=False):
        st.text_area("Normalized Text:", cleaned_text, height=250)


# ----------------------------------------------------
# TAB 5: DOWNLOADABLE ANALYSIS REPORT
# ----------------------------------------------------
with tab_export:
    st.markdown("### 📥 Export Comprehensive Evaluation Report")
    st.write("Generate and download a complete text summary of your resume evaluation and customized 4-week roadmap.")

    if target_role:
        report_text = generate_download_report(
            resume_meta=parse_result,
            detected_skills=detected_skills,
            match_results=match_result,
            target_role_info=target_role,
            roadmap_info=roadmap,
        )

        st.text_area("Report Preview:", report_text, height=300)

        st.download_button(
            label="💾 Download Evaluation Report (.txt)",
            data=report_text,
            file_name=f"resume_analysis_{target_role['role_title'].lower().replace(' ', '_')}.txt",
            mime="text/plain",
        )
