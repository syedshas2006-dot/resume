"""
Skill Extractor Module for AI Resume Analyzer
=============================================
Loads the skill taxonomy from CSV, applies regex and alias-aware token matching
on normalized resume text, and categorizes identified technical skills.
"""

import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import pandas as pd


DEFAULT_DICT_PATH = os.path.join(os.path.dirname(__file__), "data", "skill_dictionary.csv")


class SkillExtractor:
    """
    Extracts and categorizes technical competencies from cleaned resume text.
    """

    def __init__(self, dictionary_path: Optional[str] = None):
        """
        Initializes the skill extractor by loading the skill dictionary.
        
        Args:
            dictionary_path (Optional[str]): Path to skill_dictionary.csv
        """
        self.dictionary_path = dictionary_path or DEFAULT_DICT_PATH
        self.skills_df = self._load_dictionary()
        self._compile_patterns()

    def _load_dictionary(self) -> pd.DataFrame:
        """
        Loads skill dictionary from CSV with error handling and fallback defaults.
        """
        if os.path.exists(self.dictionary_path):
            try:
                df = pd.read_csv(self.dictionary_path)
                # Ensure expected columns exist
                required_cols = {"skill_name", "category", "aliases"}
                if required_cols.issubset(df.columns):
                    return df
            except Exception as e:
                print(f"Warning: Failed to load {self.dictionary_path}: {e}")

        # Fallback in-memory catalog if file is missing/corrupted
        fallback_data = [
            {"skill_name": "Python", "category": "Programming Languages", "aliases": "python|py"},
            {"skill_name": "SQL", "category": "Programming Languages", "aliases": "sql"},
            {"skill_name": "C++", "category": "Programming Languages", "aliases": r"c\+\+|cpp"},
            {"skill_name": "C#", "category": "Programming Languages", "aliases": r"c#|csharp"},
            {"skill_name": "Machine Learning", "category": "Machine Learning & AI", "aliases": "machine learning|ml"},
            {"skill_name": "Deep Learning", "category": "Machine Learning & AI", "aliases": "deep learning|dl"},
            {"skill_name": "NLP", "category": "Natural Language Processing", "aliases": "nlp|natural language processing"},
            {"skill_name": "Computer Vision", "category": "Computer Vision", "aliases": "computer vision|cv"},
            {"skill_name": "OpenCV", "category": "Computer Vision", "aliases": "opencv|cv2"},
            {"skill_name": "Pandas", "category": "Data Science & Analytics", "aliases": "pandas"},
            {"skill_name": "NumPy", "category": "Data Science & Analytics", "aliases": "numpy"},
            {"skill_name": "Tableau", "category": "Data Science & Analytics", "aliases": "tableau"},
            {"skill_name": "Power BI", "category": "Data Science & Analytics", "aliases": "power bi|powerbi"},
            {"skill_name": "Scikit-Learn", "category": "Frameworks & Libraries", "aliases": "scikit-learn|sklearn"},
            {"skill_name": "PyTorch", "category": "Frameworks & Libraries", "aliases": "pytorch|torch"},
            {"skill_name": "TensorFlow", "category": "Frameworks & Libraries", "aliases": "tensorflow|tf"},
            {"skill_name": "Git", "category": "Cloud & DevOps & Tools", "aliases": "git"},
            {"skill_name": "Docker", "category": "Cloud & DevOps & Tools", "aliases": "docker"},
        ]
        return pd.DataFrame(fallback_data)

    def _compile_patterns(self):
        """
        Pre-compiles regular expressions for each skill to ensure high extraction speed.
        """
        self.compiled_rules = []
        for _, row in self.skills_df.iterrows():
            skill_name = str(row["skill_name"]).strip()
            category = str(row["category"]).strip()
            aliases_str = str(row["aliases"]).strip() if pd.notna(row["aliases"]) else skill_name.lower()

            # Split aliases
            alias_list = [a.strip() for a in aliases_str.split("|") if a.strip()]
            if skill_name.lower() not in alias_list:
                alias_list.append(re.escape(skill_name.lower()))

            patterns = []
            for alias in alias_list:
                # Handle special technical tokens
                if alias == r"c\+\+" or alias == "c++":
                    patterns.append(r"\bc\+\+(?!\w)")
                elif alias == "c#" or alias == r"c#":
                    patterns.append(r"\bc#(?!\w)")
                elif alias == r"\.net" or alias == ".net":
                    patterns.append(r"(?:^|[\s,;])\.net(?!\w)")
                elif alias == r"\br\b" or alias == "r":
                    # Only match 'r' in programming/analytics phrases or standalone with language context
                    patterns.append(r"\b(?:r\s+programming|r\s+language|r\s+scripting|\br\b)")
                elif alias == r"\bgo\b" or alias == "go":
                    patterns.append(r"\b(?:golang|go\s+language|\bgo\b)")
                elif alias.startswith(r"\b") or alias.endswith(r"\b"):
                    patterns.append(alias)
                else:
                    escaped = re.escape(alias)
                    patterns.append(rf"\b{escaped}\b")

            combined_pattern = re.compile("|".join(patterns), re.IGNORECASE)
            self.compiled_rules.append({
                "skill_name": skill_name,
                "category": category,
                "regex": combined_pattern,
            })

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Scans normalized resume text and identifies all present skills.
        
        Args:
            text (str): Cleaned resume text
            
        Returns:
            Dict[str, Any]: {
                "detected_skills": List[str],
                "skills_by_category": Dict[str, List[str]],
                "total_skills_count": int,
                "category_counts": Dict[str, int]
            }
        """
        if not text:
            return {
                "detected_skills": [],
                "skills_by_category": {},
                "total_skills_count": 0,
                "category_counts": {},
            }

        detected: Set[str] = set()
        by_category: Dict[str, List[str]] = {}

        for rule in self.compiled_rules:
            skill = rule["skill_name"]
            cat = rule["category"]
            if rule["regex"].search(text):
                detected.add(skill)
                if cat not in by_category:
                    by_category[cat] = []
                if skill not in by_category[cat]:
                    by_category[cat].append(skill)

        sorted_skills = sorted(list(detected))
        # Sort skills within each category
        for cat in by_category:
            by_category[cat].sort()

        category_counts = {cat: len(skills) for cat, skills in by_category.items()}

        return {
            "detected_skills": sorted_skills,
            "skills_by_category": by_category,
            "total_skills_count": len(sorted_skills),
            "category_counts": category_counts,
        }
