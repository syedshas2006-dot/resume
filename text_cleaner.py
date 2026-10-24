"""
Text Cleaner Module for AI Resume Analyzer
==========================================
Cleans, sanitizes, and normalizes raw text extracted from PDF/DOCX resumes.
Preserves critical technical terms like C++, C#, .NET, SQL, CI/CD, Node.js, etc.
Excludes demographic attributes (gender, age, marital status, religion, nationality)
to ensure fair, skill-focused evaluation.
"""

import re
import unicodedata
from typing import Dict, List

# Technical terms that contain symbols which standard punctuation removal would destroy.
# Note: Characters like +, #, . are non-word characters, so we avoid trailing \b and use (?!\w).
PROTECTED_TERMS: Dict[str, str] = {
    r"\bc\+\+(?!\w)": " TOKENXYZCPPXYZ ",
    r"\bc#(?!\w)": " TOKENXYZCSHARPXYZ ",
    r"(?:^|[\s,;])\.net(?!\w)": " TOKENXYZDOTNETXYZ ",
    r"\bci/cd(?!\w)": " TOKENXYZCICDXYZ ",
    r"\bnode\.js(?!\w)": " TOKENXYZNODEJSXYZ ",
    r"\bvue\.js(?!\w)": " TOKENXYZVUEJSXYZ ",
    r"\ba/b\s+testing(?!\w)": " TOKENXYZABTESTINGXYZ ",
    r"\btf-idf(?!\w)": " TOKENXYZTFIDFXYZ ",
    r"\btcp/ip(?!\w)": " TOKENXYZTCPIPXYZ ",
    r"\bpl/sql(?!\w)": " TOKENXYZPLSQLXYZ ",
    r"\bscikit-learn(?!\w)": " TOKENXYZSKLEARNXYZ ",
    r"\bhugging\s+face(?!\w)": " TOKENXYZHUGGINGFACEXYZ ",
}

RESTORE_MAP: Dict[str, str] = {
    "tokenxyzcppxyz": "c++",
    "tokenxyzcsharpxyz": "c#",
    "tokenxyzdotnetxyz": ".net",
    "tokenxyzcicdxyz": "ci/cd",
    "tokenxyznodejsxyz": "node.js",
    "tokenxyzvuejsxyz": "vue.js",
    "tokenxyzabtestingxyz": "a/b testing",
    "tokenxyztfidfxyz": "tf-idf",
    "tokenxyztcpipxyz": "tcp/ip",
    "tokenxyzplsqlxyz": "pl/sql",
    "tokenxyzsklearnxyz": "scikit-learn",
    "tokenxyzhuggingfacexyz": "hugging face",
}

# Sensitive/demographic keywords to neutralize from scoring
SENSITIVE_PATTERNS: List[str] = [
    r"\b(male|female|gender|transgender|non-binary)\b",
    r"\b(marital\s*status|married|single|unmarried|divorced)\b",
    r"\b(religion|hindu|muslim|christian|sikh|jain|buddhist)\b",
    r"\b(date\s*of\s*birth|dob|age\s*:\s*\d{1,2}|\b\d{1,2}\s+years\s+old)\b",
    r"\b(nationality|indian|american|canadian|citizen)\b",
    r"\b(disability|handicap|pwd)\b",
    r"\b(photograph|photo\s+attached|passport\s+size\s+photo)\b",
]


def clean_text(text: str, remove_sensitive: bool = True) -> str:
    """
    Primary text normalization pipeline:
    1. Normalize Unicode (e.g. smart quotes, em dashes, non-breaking spaces)
    2. Optional: Redact demographic/sensitive sections to prevent bias
    3. Protect special programming terms (C++, C#, .NET, CI/CD, etc.)
    4. Strip URLs, emails, phone numbers, and control characters
    5. Remove generic punctuation while preserving technical tokens
    6. Normalize whitespace and restore protected terms
    
    Args:
        text (str): Raw string extracted from resume
        remove_sensitive (bool): Flag to redact demographic tokens
        
    Returns:
        str: Cleaned, normalized lowercase text ready for NLP extraction
    """
    if not text or not isinstance(text, str):
        return ""

    # Step 1: Normalize unicode characters (NFKD)
    normalized = unicodedata.normalize("NFKD", text)

    # Step 2: Neutralize common demographic sections if requested
    if remove_sensitive:
        for pattern in SENSITIVE_PATTERNS:
            normalized = re.sub(pattern, " ", normalized, flags=re.IGNORECASE)

    # Step 3: Remove email addresses and URLs (privacy and noise reduction)
    normalized = re.sub(r"\S+@\S+\.\S+", " ", normalized)
    normalized = re.sub(r"https?://\S+|www\.\S+", " ", normalized)
    normalized = re.sub(r"\b\d{10,12}\b", " ", normalized)  # Phone numbers

    # Step 4: Protect special programming terms
    protected = normalized
    for pattern, placeholder in PROTECTED_TERMS.items():
        protected = re.sub(pattern, placeholder, protected, flags=re.IGNORECASE)

    # Step 5: Replace bullets, symbols, and formatting noise
    cleaned = re.sub(r"[•▪►★●◆♦–—_~|\\<>{}\[\]\(\)\"\'`:;!?*,./#+]", " ", protected)

    # Step 6: Convert to lowercase
    cleaned_lower = cleaned.lower()

    # Step 7: Restore protected technical terms
    restored = cleaned_lower
    for placeholder, term in RESTORE_MAP.items():
        restored = restored.replace(placeholder, term)

    # Step 8: Collapse multiple spaces, tabs, and newlines into single spaces
    normalized_spaces = re.sub(r"\s+", " ", restored).strip()

    return normalized_spaces


def extract_sections(text: str) -> Dict[str, str]:
    """
    Heuristically splits resume text into common sections if present:
    Skills, Experience, Education, Projects, Summary.
    
    Args:
        text (str): Raw or semi-cleaned resume text
        
    Returns:
        Dict[str, str]: Mapping of section name to section content
    """
    sections = {
        "summary": "",
        "skills": "",
        "experience": "",
        "projects": "",
        "education": "",
        "certifications": "",
    }
    
    if not text:
        return sections
        
    lines = text.split("\n")
    current_section = "summary"
    
    section_patterns = {
        "skills": r"\b(technical\s+skills|skills|technologies|core\s+competencies|tools)\b",
        "experience": r"\b(work\s+experience|experience|employment\s+history|internship|internships)\b",
        "projects": r"\b(projects|academic\s+projects|key\s+projects)\b",
        "education": r"\b(education|academic\s+background|qualifications)\b",
        "certifications": r"\b(certifications|certificates|courses)\b",
    }
    
    for line in lines:
        stripped = line.strip()
        matched = False
        for sec, pattern in section_patterns.items():
            if re.match(pattern, stripped, re.IGNORECASE) and len(stripped.split()) <= 4:
                current_section = sec
                matched = True
                break
        if not matched and stripped:
            sections[current_section] += " " + stripped
            
    return {k: v.strip() for k, v in sections.items()}
