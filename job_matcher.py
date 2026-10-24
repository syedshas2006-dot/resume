"""
Job Matcher Module for AI Resume Analyzer
=========================================
Computes text similarity and skill overlap between candidate resume text
and target job profiles using TF-IDF vectorization and Cosine Similarity.
Generates ranked recommendations and detailed gap analysis.
"""

import os
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DEFAULT_JOB_ROLES_PATH = os.path.join(os.path.dirname(__file__), "data", "job_roles.csv")

DISCLAIMER_TEXT = (
    "Note: The match score is an estimated text-similarity score based on keyword and "
    "contextual TF-IDF matching. It is NOT a hiring probability or a guarantee of employment. "
    "Missing keywords do not necessarily indicate a lack of practical competency."
)


class JobMatcher:
    """
    Ranks job roles and computes detailed match scores against resumes.
    """

    def __init__(self, job_roles_path: Optional[str] = None):
        """
        Initializes the matcher with job role profiles.
        
        Args:
            job_roles_path (Optional[str]): Path to job_roles.csv
        """
        self.job_roles_path = job_roles_path or DEFAULT_JOB_ROLES_PATH
        self.roles_df = self._load_job_roles()
        # Custom token pattern preserves +, #, ., / inside tokens (e.g. c++, c#, .net, ci/cd)
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            token_pattern=r"(?u)\b[\w\+\#\./\-]+\b",
            max_features=5000,
        )

    def _load_job_roles(self) -> pd.DataFrame:
        """
        Loads job roles from CSV or provides fallback built-in roles.
        """
        if os.path.exists(self.job_roles_path):
            try:
                df = pd.read_csv(self.job_roles_path)
                required = {"role_id", "role_title", "overview", "required_skills", "description"}
                if required.issubset(df.columns):
                    return df
            except Exception as e:
                print(f"Warning: Failed to load {self.job_roles_path}: {e}")

        # Fallback data
        fallback = [
            {
                "role_id": 1,
                "role_title": "Data Analyst",
                "overview": "Transforms raw data into actionable business insights.",
                "required_skills": "Python, SQL, Data Analysis, Pandas, NumPy, Tableau, Power BI, Excel, Statistics",
                "description": "Seeking a Data Analyst with strong SQL, Python, Pandas, Tableau, and Excel skills.",
                "experience_level": "Entry to Mid Level",
            },
            {
                "role_id": 2,
                "role_title": "Machine Learning Engineer",
                "overview": "Designs, trains, and deploys predictive machine learning models.",
                "required_skills": "Python, Machine Learning, Scikit-Learn, Pandas, NumPy, Model Deployment, Git, Docker, Statistics",
                "description": "ML Engineer experienced in supervised learning, Scikit-Learn, feature engineering, and model deployment.",
                "experience_level": "Mid Level",
            },
            {
                "role_id": 3,
                "role_title": "AI Engineer",
                "overview": "Builds intelligent AI systems with deep learning and LLMs.",
                "required_skills": "Python, Deep Learning, Neural Networks, PyTorch, TensorFlow, Transformers, Large Language Models, Generative AI, Docker, AWS",
                "description": "AI Engineer to build modern AI solutions with PyTorch, transformers, generative AI, LLMs, and cloud.",
                "experience_level": "Mid to Senior Level",
            },
            {
                "role_id": 4,
                "role_title": "NLP Engineer",
                "overview": "Specializes in text processing, linguistic models, and language understanding.",
                "required_skills": "Python, NLP, Tokenization, TF-IDF, BERT, GPT, Hugging Face, NLTK, SpaCy, Text Classification, Scikit-Learn",
                "description": "NLP Engineer to build text analytics, transformers, BERT, text classification, and sentiment analysis.",
                "experience_level": "Mid Level",
            },
            {
                "role_id": 5,
                "role_title": "Computer Vision Engineer",
                "overview": "Develops computer vision, object detection, and visual perception systems.",
                "required_skills": "Python, Computer Vision, OpenCV, Image Processing, Object Detection, YOLO, CNN, ResNet, Deep Learning, PyTorch",
                "description": "Computer Vision Engineer specializing in OpenCV, YOLO object detection, image segmentation, and CNNs.",
                "experience_level": "Mid Level",
            },
        ]
        return pd.DataFrame(fallback)

    def _parse_required_skills(self, skills_str: str) -> List[str]:
        """
        Parses comma-separated skill string into a normalized, clean list.
        """
        if not skills_str or pd.isna(skills_str):
            return []
        return [s.strip() for s in str(skills_str).split(",") if s.strip()]

    def match_resume(self, resume_text: str, detected_skills: List[str]) -> Dict[str, Any]:
        """
        Compares resume text and detected skills with all job roles.
        
        Args:
            resume_text (str): Cleaned resume text
            detected_skills (List[str]): Extracted skills from resume
            
        Returns:
            Dict[str, Any]: Comprehensive matching results with ranking and breakdown.
        """
        detected_set = {s.lower() for s in detected_skills}
        role_results = []

        # Prepare corpus for TF-IDF: [resume_text, role_text_1, role_text_2, ...]
        role_texts = []
        for _, row in self.roles_df.iterrows():
            comb = f"{row['role_title']} {row['overview']} {row['required_skills']} {row['description']}"
            role_texts.append(comb)

        corpus = [resume_text] + role_texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            # Compute cosine similarities between resume vector (index 0) and each role vector (index 1 to N)
            resume_vec = tfidf_matrix[0:1]
            roles_vecs = tfidf_matrix[1:]
            similarities = cosine_similarity(resume_vec, roles_vecs)[0]
        except Exception as e:
            # Fallback if vocabulary is too sparse or empty
            similarities = [0.0] * len(self.roles_df)

        for idx, (_, row) in enumerate(self.roles_df.iterrows()):
            role_title = str(row["role_title"])
            required_skills = self._parse_required_skills(row["required_skills"])
            
            # Skill overlap
            matched_skills = []
            missing_skills = []
            for req in required_skills:
                if req.lower() in detected_set:
                    matched_skills.append(req)
                else:
                    missing_skills.append(req)

            total_req = len(required_skills)
            skill_pct = round((len(matched_skills) / total_req * 100), 1) if total_req > 0 else 0.0
            
            # TF-IDF similarity (0.0 to 1.0 -> 0 to 100)
            sim_score = max(0.0, float(similarities[idx]))
            tfidf_pct = round(sim_score * 100, 1)

            # Combined estimated match score: 55% skill overlap + 45% textual/context similarity
            estimated_score = round((0.55 * skill_pct) + (0.45 * tfidf_pct), 1)
            estimated_score = min(100.0, max(0.0, estimated_score))

            role_results.append({
                "role_id": int(row["role_id"]),
                "role_title": role_title,
                "overview": str(row["overview"]),
                "experience_level": str(row.get("experience_level", "All Levels")),
                "estimated_match_score": estimated_score,
                "skill_match_percentage": skill_pct,
                "tfidf_similarity_percentage": tfidf_pct,
                "matched_skills": sorted(matched_skills),
                "missing_skills": sorted(missing_skills),
                "required_skills": required_skills,
                "matched_count": len(matched_skills),
                "total_required_count": total_req,
            })

        # Rank roles by estimated match score descending
        ranked_roles = sorted(role_results, key=lambda x: x["estimated_match_score"], reverse=True)
        top_3 = ranked_roles[:3]

        return {
            "all_roles": ranked_roles,
            "top_3_recommendations": top_3,
            "best_match_role": top_3[0] if top_3 else None,
            "total_roles_evaluated": len(ranked_roles),
            "disclaimer": DISCLAIMER_TEXT,
        }

    def get_role_deep_dive(self, results: Dict[str, Any], selected_role_title: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves detailed comparison metrics for a specific chosen role.
        """
        for role in results.get("all_roles", []):
            if role["role_title"].lower() == selected_role_title.lower():
                return role
        return None
