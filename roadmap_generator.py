"""
Roadmap Generator Module for AI Resume Analyzer
===============================================
Generates a structured, beginner-friendly 4-week learning roadmap
tailored to bridge the candidate's detected skill gaps for any chosen job role.
Includes free learning resources, practical milestone tasks, and portfolio suggestions.
"""

from typing import Any, Dict, List, Optional


# Curated knowledge base mapping specific skills to practical learning resources and topics
SKILL_LEARNING_GUIDE: Dict[str, Dict[str, Any]] = {
    "Python": {
        "concept": "Python Data Structures, Functions, and OOP",
        "resource": "Official Python Tutorial (docs.python.org) & Automate the Boring Stuff",
        "practice": "Write scripts manipulating lists/dictionaries and reading CSV files.",
    },
    "SQL": {
        "concept": "SQL SELECT, JOINs, GROUP BY, Window Functions, and Indexing",
        "resource": "Mode Analytics SQL Tutorial & SQLZoo.net (Free)",
        "practice": "Write multi-table aggregate queries and window functions on sample datasets.",
    },
    "Pandas": {
        "concept": "DataFrames, Series, filtering, grouping, merging, and missing data imputation",
        "resource": "10 Minutes to pandas (pandas.pydata.org) & Kaggle Pandas Micro-course",
        "practice": "Clean and aggregate real-world messy CSV datasets into tidy DataFrames.",
    },
    "NumPy": {
        "concept": "N-dimensional arrays, vectorization, broadcasting, and matrix math",
        "resource": "NumPy Absolute Beginner Guide (numpy.org)",
        "practice": "Replace Python for-loops with vectorized NumPy array computations.",
    },
    "Data Analysis": {
        "concept": "Exploratory Data Analysis (EDA), distribution analysis, anomaly detection",
        "resource": "Kaggle EDA Guides & Google Data Analytics Certificate insights",
        "practice": "Perform a complete EDA on a dataset from Kaggle or data.gov.",
    },
    "Data Visualization": {
        "concept": "Visual storytelling, chart selection, readability, and dashboard layout",
        "resource": "Data-to-Viz.com & Storytelling with Data",
        "practice": "Build 5 diverse charts (scatter, bar, box, heatmap, line) communicating insights.",
    },
    "Matplotlib": {
        "concept": "Figure & axes hierarchy, subplots, annotations, and styling",
        "resource": "Matplotlib official tutorials (matplotlib.org)",
        "practice": "Create multi-panel comparison plots with custom color palettes and annotations.",
    },
    "Seaborn": {
        "concept": "Statistical plotting: pairplots, distribution plots, heatmaps, categorical plots",
        "resource": "Seaborn documentation gallery (seaborn.pydata.org)",
        "practice": "Visualize feature correlations and distribution skewness in a single view.",
    },
    "Tableau": {
        "concept": "Connecting data sources, calculated fields, parameters, interactive dashboards",
        "resource": "Tableau Public Free Video Training (tableau.com/learn)",
        "practice": "Build an interactive sales or marketing dashboard published to Tableau Public.",
    },
    "Power BI": {
        "concept": "Power Query ETL, Data Modeling (Star Schema), DAX measures, visual reports",
        "resource": "Microsoft Learn: Power BI Fundamentals (learn.microsoft.com)",
        "practice": "Create an automated reporting dashboard with drill-through filters and DAX KPIs.",
    },
    "Excel": {
        "concept": "XLOOKUP, Pivot Tables, Conditional Formatting, Power Query, basic macros",
        "resource": "ExcelJet.net tutorials & Chandoo.org",
        "practice": "Consolidate multiple monthly sheets into an automated pivot table summary.",
    },
    "Statistics": {
        "concept": "Descriptive statistics, normal distribution, hypothesis testing, p-values, confidence intervals",
        "resource": "Khan Academy Statistics & Probability / StatQuest by Josh Starmer",
        "practice": "Calculate standard error, run a t-test, and interpret significance on sample data.",
    },
    "Machine Learning": {
        "concept": "Supervised vs. Unsupervised learning, train/test split, overfitting, bias-variance tradeoff",
        "resource": "StatQuest ML Playlist & Andrew Ng's Machine Learning Specialization notes",
        "practice": "Implement a baseline classification and regression model pipeline from scratch.",
    },
    "Scikit-Learn": {
        "concept": "Estimator API, Pipeline, StandardScaler, GridSearchCV, cross_val_score",
        "resource": "Scikit-Learn User Guide (scikit-learn.org)",
        "practice": "Build an end-to-end ML pipeline with preprocessing, imputation, and cross-validation.",
    },
    "Deep Learning": {
        "concept": "Forward pass, backpropagation, activation functions (ReLU), loss functions, optimizers (Adam)",
        "resource": "Fast.ai Practical Deep Learning for Coders & 3Blue1Brown Neural Networks",
        "practice": "Train a multi-layer perceptron on tabular or digit image data.",
    },
    "Neural Networks": {
        "concept": "Perceptrons, weights, biases, gradient descent, vanishing gradients, regularizers",
        "resource": "DeepLearning.AI Deep Learning Specialization summaries",
        "practice": "Build and train a 2-layer neural network using NumPy to understand gradients.",
    },
    "PyTorch": {
        "concept": "Tensors, autograd, nn.Module, DataLoader, training loops, GPU acceleration",
        "resource": "PyTorch 60-Minute Blitz (pytorch.org/tutorials)",
        "practice": "Write an explicit training and validation loop for a PyTorch classifier.",
    },
    "TensorFlow": {
        "concept": "Keras Sequential/Functional APIs, callbacks, TensorBoard, SavedModel",
        "resource": "TensorFlow Official Tutorials (tensorflow.org/tutorials)",
        "practice": "Train a deep neural network with early stopping and learning rate scheduling callbacks.",
    },
    "Transformers": {
        "concept": "Self-attention mechanism, multi-head attention, positional encoding, encoder-decoder",
        "resource": "The Illustrated Transformer by Jay Alammar & Hugging Face NLP Course",
        "practice": "Inspect attention weights and tokenize text using a pretrained transformer.",
    },
    "Large Language Models": {
        "concept": "Token generation, temperature, context windows, few-shot prompting, RLHF, quantization",
        "resource": "Hugging Face LLM Course & DeepLearning.AI Generative AI courses",
        "practice": "Construct structured prompt templates with few-shot examples for structured outputs.",
    },
    "Generative AI": {
        "concept": "Autoregressive generation, diffusion models, embeddings, RAG architectures",
        "resource": "LangChain & LlamaIndex documentation, Google Cloud GenAI tutorials",
        "practice": "Build a document Q&A assistant connecting local documents to an embedding retriever.",
    },
    "NLP": {
        "concept": "Text preprocessing, stopwords, n-grams, bag of words, sentiment classification",
        "resource": "NLTK Book (nltk.org/book) & SpaCy Course (course.spacy.io)",
        "practice": "Preprocess a collection of customer reviews and train a text sentiment classifier.",
    },
    "Computer Vision": {
        "concept": "Image representations, color spaces, convolutions, edge detection, filtering",
        "resource": "OpenCV-Python Tutorials (docs.opencv.org) & CS231n notes",
        "practice": "Apply Gaussian blurring, Sobel edge filters, and contour detection to images.",
    },
    "OpenCV": {
        "concept": "cv2.imread, color conversion, geometric transforms, thresholding, morphology",
        "resource": "OpenCV official documentation & PyImageSearch tutorials",
        "practice": "Build a webcam or image filter script detecting dominant colors and object boundaries.",
    },
    "YOLO": {
        "concept": "One-stage object detection, bounding box regression, anchor boxes, IoU, mAP",
        "resource": "Ultralytics YOLO Docs (docs.ultralytics.com)",
        "practice": "Run inference with pretrained YOLOv8 on custom photos and count detected classes.",
    },
    "Docker": {
        "concept": "Containers vs. VMs, Dockerfile, images, volumes, port forwarding",
        "resource": "Docker Get Started Guide (docs.docker.com/get-started)",
        "practice": "Write a Dockerfile to containerize a Python Flask or FastAPI inference script.",
    },
    "Git": {
        "concept": "git init, add, commit, branch, merge, pull requests, resolving conflicts",
        "resource": "Pro Git Book (git-scm.com/book) & GitHub Skills interactive courses",
        "practice": "Create a GitHub repository, push your project code, and create feature branches.",
    },
    "AWS": {
        "concept": "S3 buckets, EC2 virtual servers, IAM roles, Lambda serverless functions",
        "resource": "AWS Free Tier & AWS Skill Builder cloud practitioner modules",
        "practice": "Deploy a lightweight Python microservice to AWS Lambda or EC2.",
    },
    "FastAPI": {
        "concept": "ASGI, Pydantic schemas, path parameters, dependency injection, automatic Swagger docs",
        "resource": "FastAPI Tutorial (fastapi.tiangolo.com/tutorial)",
        "practice": "Create an API endpoint that accepts JSON input and returns model predictions.",
    },
}


def generate_roadmap(target_role: str, missing_skills: List[str], matched_skills: List[str]) -> Dict[str, Any]:
    """
    Constructs a beginner-friendly, structured 4-week learning roadmap.
    
    Args:
        target_role (str): Target job profile (e.g. 'Data Analyst', 'Machine Learning Engineer')
        missing_skills (List[str]): List of skills not detected in resume
        matched_skills (List[str]): List of detected matching skills
        
    Returns:
        Dict[str, Any]: Detailed 4-week learning roadmap with weekly deliverables.
    """
    total_missing = len(missing_skills)

    # Scenario A: Candidate already has all required skills
    if total_missing == 0:
        return _generate_mastery_roadmap(target_role, matched_skills)

    # Scenario B: Distribute missing skills across 4 progressive weeks
    # Week 1: Core Fundamentals & Data Layer
    # Week 2: Key Frameworks & Practical Tooling
    # Week 3: Applied Modeling & Workflow Pipelines
    # Week 4: Capstone Portfolio Project & Interview Prep
    
    w1_skills: List[str] = []
    w2_skills: List[str] = []
    w3_skills: List[str] = []
    w4_skills: List[str] = []

    for idx, skill in enumerate(missing_skills):
        bucket = idx % 4
        if bucket == 0:
            w1_skills.append(skill)
        elif bucket == 1:
            w2_skills.append(skill)
        elif bucket == 2:
            w3_skills.append(skill)
        else:
            w4_skills.append(skill)

    # Helper to generate task descriptions
    def build_tasks(skills: List[str], week_num: int) -> List[Dict[str, str]]:
        tasks = []
        if not skills:
            tasks.append({
                "title": f"Review & consolidate your existing strengths ({', '.join(matched_skills[:3]) if matched_skills else 'core fundamentals'})",
                "concept": "Deepen foundational problem-solving and code readability.",
                "resource": "FreeCodeCamp & LeetCode (Easy algorithmic practice)",
                "action": "Complete 3 problem-solving exercises related to this domain.",
            })
            return tasks

        for s in skills:
            info = SKILL_LEARNING_GUIDE.get(s, {
                "concept": f"Master the core syntax, APIs, and real-world usage of {s}.",
                "resource": f"Official documentation and beginner tutorials for {s}.",
                "practice": f"Build a practical exercise or mini-script utilizing {s}.",
            })
            tasks.append({
                "title": f"Learn & Apply {s}",
                "concept": info["concept"],
                "resource": info["resource"],
                "action": info["practice"],
            })
        return tasks

    weeks = [
        {
            "week_number": 1,
            "title": "Week 1: Core Foundations & Prerequisites",
            "focus_skills": w1_skills,
            "goal": "Build conceptual clarity and set up a solid programming & theoretical foundation.",
            "deliverable": "Working baseline scripts and interactive notebooks exploring foundational concepts.",
            "tasks": build_tasks(w1_skills, 1),
        },
        {
            "week_number": 2,
            "title": "Week 2: Hands-on Tooling & Practical Implementation",
            "focus_skills": w2_skills,
            "goal": "Transition from basics to hands-on library usage and structured data processing.",
            "deliverable": "A reproducible script or data pipeline processing realistic sample inputs.",
            "tasks": build_tasks(w2_skills, 2),
        },
        {
            "week_number": 3,
            "title": "Week 3: Applied Modeling & Workflow Pipelines",
            "focus_skills": w3_skills,
            "goal": "Integrate multiple skills into cohesive end-to-end workflows with error handling.",
            "deliverable": "A fully functional mini-project implementing your target role's core logic.",
            "tasks": build_tasks(w3_skills, 3),
        },
        {
            "week_number": 4,
            "title": "Week 4: Capstone Portfolio Project & Interview Readiness",
            "focus_skills": w4_skills,
            "goal": "Publish an end-to-end portfolio project to GitHub and prepare STAR-method interview responses.",
            "deliverable": "A documented GitHub repository with README, demo screenshots, and clean code.",
            "tasks": build_tasks(w4_skills, 4),
        },
    ]

    return {
        "target_role": target_role,
        "is_mastery_mode": False,
        "total_skills_to_learn": total_missing,
        "missing_skills": missing_skills,
        "weeks": weeks,
        "summary": (
            f"Personalized 4-Week Roadmap designed to bridge {total_missing} missing skill(s) "
            f"for the '{target_role}' role. Dedicate 60-90 minutes daily for maximum progress."
        ),
    }


def _generate_mastery_roadmap(target_role: str, matched_skills: List[str]) -> Dict[str, Any]:
    """
    Generates an advanced mastery roadmap when candidate already matches all required keywords.
    """
    weeks = [
        {
            "week_number": 1,
            "title": "Week 1: Production Engineering & Code Quality",
            "focus_skills": ["Clean Code", "Unit Testing", "CI/CD"],
            "goal": "Elevate scripts to modular production-grade code with pytest and linting.",
            "deliverable": "Automated GitHub Actions CI workflow running tests on push.",
            "tasks": [
                {
                    "title": "Refactor Code into Python Modules & Packages",
                    "concept": "Type hints, docstrings, modular functions, and PEP 8 standards.",
                    "resource": "Real Python: Python Code Quality Tools & Best Practices",
                    "action": "Refactor previous scripts with mypy and flake8.",
                },
                {
                    "title": "Write Automated Unit Tests",
                    "concept": "Unit testing, mocking APIs, edge case assertions.",
                    "resource": "pytest documentation (docs.pytest.org)",
                    "action": "Achieve 80%+ test coverage for your core logic.",
                },
            ],
        },
        {
            "week_number": 2,
            "title": "Week 2: Scalability, Latency & Optimization",
            "focus_skills": ["Vectorization", "Caching", "Async Pipelines"],
            "goal": "Benchmark algorithms, reduce execution latency, and eliminate bottlenecks.",
            "deliverable": "Performance benchmark report showing 2x-5x latency improvements.",
            "tasks": [
                {
                    "title": "Profiling & Bottleneck Identification",
                    "concept": "cProfile, line_profiler, memory profiling.",
                    "resource": "Python Speed & Optimization Guides",
                    "action": "Profile memory and CPU bottlenecks on large datasets.",
                },
            ],
        },
        {
            "week_number": 3,
            "title": "Week 3: Containerization & Cloud Deployment",
            "focus_skills": ["Docker", "Cloud APIs", "Monitoring"],
            "goal": "Package the solution in Docker and deploy to a cloud container runtime.",
            "deliverable": "A live hosted API or interactive demo on cloud infrastructure.",
            "tasks": [
                {
                    "title": "Multi-stage Docker Containerization",
                    "concept": "Lightweight alpine/slim images, non-root users, layer caching.",
                    "resource": "Docker Best Practices Guide",
                    "action": "Build a sub-200MB Docker image running your model API.",
                },
            ],
        },
        {
            "week_number": 4,
            "title": "Week 4: Technical Storytelling & Senior Interview Prep",
            "focus_skills": ["System Design", "Behavioral STAR", "Portfolio Polish"],
            "goal": "Prepare architectural diagrams and articulate trade-offs in interviews.",
            "deliverable": "Polished README with architecture diagrams, metrics, and live demo link.",
            "tasks": [
                {
                    "title": "System Design Architecture & Trade-offs",
                    "concept": "Trade-offs between latency, cost, accuracy, and maintainability.",
                    "resource": "ByteByteGo System Design & GitHub Primer",
                    "action": "Create an architectural diagram explaining your end-to-end system.",
                },
            ],
        },
    ]

    return {
        "target_role": target_role,
        "is_mastery_mode": True,
        "total_skills_to_learn": 0,
        "missing_skills": [],
        "weeks": weeks,
        "summary": (
            f"You have detected matches for all required skills for '{target_role}'! "
            f"This 4-Week Advanced Mastery Roadmap focuses on production scaling, system design, and interview storytelling."
        ),
    }
