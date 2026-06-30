# Local Skill Prerequisite Graph for SkillBridge AI
# Provides prerequisite chaining and flexible tech/non-tech learning paths.

# Mappings of target interest zones to recommended positions (AI + leading tech roles) and their core skill requirements
INTEREST_ROLES = {
    "Building AI Products": {
        "AI Product Support": ["Prompt Engineering", "API Fundamentals", "Customer Support", "Basic Troubleshooting"],
        "LLM Evaluation Specialist": ["Prompt Engineering", "LLM Fundamentals", "Model Evaluation Metrics", "Data Labeling"],
        "Full-Stack AI Developer": ["Frontend Basics", "Backend Basics", "API Integration", "Python", "LLM Orchestration"]
    },
    "Data & Analytics": {
        "Data Quality Analyst": ["SQL Basics", "Data Auditing", "Excel Advanced", "Data Cleaning"],
        "AI Data Pipeline Engineer": ["Python", "SQL Basics", "Apache Spark", "Vector Databases", "Data Engineering"],
        "Data Architect": ["SQL Basics", "Data Modeling", "Data Engineering", "Cloud Warehouses", "Python"]
    },
    "AI Safety & Governance": {
        "AI Compliance Officer": ["AI Ethics Basics", "Regulatory Frameworks", "Risk Assessment", "Audit Logging"],
        "AI Alignment Auditor": ["AI Ethics Basics", "Model Evaluation Metrics", "Reinforcement Learning Basics", "Red Teaming"],
        "Model Safety Evaluator": ["Prompt Engineering", "Red Teaming", "LLM Guardrails", "Toxicity Analysis"]
    },
    "AI Operations": {
        "AI Operations Specialist": ["Inference APIs", "Model Deployment", "Docker", "Monitoring Tools"],
        "DevOps / SRE Lead": ["Docker", "Kubernetes", "CI/CD Pipelines", "Monitoring Tools", "Basic Scripting"],
        "Inference Scaling Specialist": ["Docker", "Kubernetes", "vLLM Engine", "Triton Server", "Inference APIs"]
    }
}

# The dependency graph of skills (technical prerequisite chain)
# Format: skill_name: [list of prerequisite skills]
PREREQUISITES = {
    # Foundational layer
    "Python": [],
    "SQL Basics": [],
    "API Fundamentals": [],
    "Prompt Engineering": [],
    "AI Ethics Basics": [],
    "Excel Advanced": [],
    "Frontend Basics": [],
    "Backend Basics": [],
    "Basic Scripting": [],
    
    # Mid-tier conceptual/technical layer
    "LLM Fundamentals": ["Prompt Engineering"],
    "Embeddings": ["Python"],
    "Vector Databases": ["SQL Basics"],
    "Docker": [],
    "Inference APIs": ["API Fundamentals"],
    "AI Regulatory Frameworks": ["AI Ethics Basics"],
    "Red Teaming": ["Prompt Engineering"],
    "Data Labeling": [],
    "API Integration": ["API Fundamentals"],
    "Data Modeling": ["SQL Basics"],
    "CI/CD Pipelines": ["Basic Scripting"],
    "Monitoring Tools": [],
    
    # Advanced layer
    "LLM Orchestration": ["LLM Fundamentals", "Embeddings"],
    "Semantic Search": ["Vector Databases", "Embeddings"],
    "Model Evaluation Metrics": ["LLM Fundamentals"],
    "Toxicity Analysis": ["Model Evaluation Metrics"],
    "LLM Guardrails": ["Model Evaluation Metrics", "Red Teaming"],
    "Data Engineering": ["Python", "SQL Basics"],
    "Apache Spark": ["Data Engineering"],
    "Cloud Warehouses": ["Data Engineering"],
    "Index Optimization": ["Vector Databases"],
    "PEFT Techniques": ["LLM Fundamentals", "PyTorch"],
    "PyTorch": ["Python"],
    "GPU Memory Management": ["PyTorch"],
    "vLLM Engine": ["Model Deployment", "Docker"],
    "Triton Server": ["Model Deployment", "Docker"],
    "Model Deployment": ["Inference APIs", "Docker"],
    "Kubernetes": ["Docker"],
    "Risk Assessment": ["AI Ethics Basics"],
    "Audit Logging": ["SQL Basics"],
    "Data Auditing": ["SQL Basics", "Data Cleaning"],
    "Data Cleaning": []
}

# Human-friendly descriptions and entry-level pathways for non-tech users
NON_TECH_FRIENDLY = {
    "Python": "Python Basics (Writing simple programs and script logic)",
    "SQL Basics": "SQL Basics (Querying databases and retrieving data)",
    "API Fundamentals": "API Fundamentals (How software programs talk to each other)",
    "Prompt Engineering": "Prompt Engineering (How to write effective instructions for AI)",
    "Vector Databases": "Vector Databases (Databases that store and search data for AI)",
    "LLM Fundamentals": "What is an LLM (Core concepts behind ChatGPT and Gemini)",
    "LLM Orchestration": "AI Orchestration (Combining AI models with other tools)",
    "Embeddings": "AI Representations (How computers translate words into numbers)",
    "Docker": "Software Containers (Packing code to run anywhere)",
    "Model Deployment": "Launching Models (Making AI models accessible on the web)",
    "Inference APIs": "Inference APIs (Getting answers from hosted AI models)",
    "AI Ethics Basics": "AI Ethics (Responsible AI, bias, and fairness)",
    "Red Teaming": "AI Safety Testing (Finding vulnerabilities by trying to break AI)",
    "Model Evaluation Metrics": "Model Evaluation (Measuring how good and accurate an AI is)",
    "Data Cleaning": "Data Cleaning (Sorting and organizing data for quality)",
    "Frontend Basics": "Web Design Basics (HTML, CSS, and basic UI design)",
    "Backend Basics": "Server Basics (How database connections and web servers work)",
    "Basic Scripting": "Basic Automation (Writing commands to perform repetitive tasks)",
    "Data Modeling": "Data Organizing (Designing tables to store records clearly)",
    "CI/CD Pipelines": "Automated Software Delivery (Automatically testing and launching code updates)"
}

def resolve_prerequisites(required_skills, is_tech=True):
    """
    Traverses the prerequisite graph for a set of target skills,
    returning a topologically sorted list of skills to build.
    If is_tech=False, adds foundational basics for any complex skill.
    """
    resolved = []
    visited = set()
    
    # If the user is non-technical, ensure foundational prerequisites are added for complex skills
    work_list = list(required_skills)
    
    def dfs(skill):
        if skill in visited:
            return
        visited.add(skill)
        
        prereqs = PREREQUISITES.get(skill, [])
        for p in prereqs:
            dfs(p)
            
        # If user is non-tech, dynamically check if we need to insert baseline concepts
        if not is_tech:
            if skill in ["Vector Databases", "Data Engineering", "Audit Logging", "Data Modeling"] and "SQL Basics" not in visited:
                dfs("SQL Basics")
            if skill in ["Embeddings", "LLM Orchestration", "PEFT Techniques", "PyTorch", "Cloud Warehouses"] and "Python" not in visited:
                dfs("Python")
            if skill in ["Inference APIs", "Model Deployment", "API Integration"] and "API Fundamentals" not in visited:
                dfs("API Fundamentals")
            if skill in ["LLM Fundamentals", "Red Teaming"] and "Prompt Engineering" not in visited:
                dfs("Prompt Engineering")
            if skill in ["CI/CD Pipelines"] and "Basic Scripting" not in visited:
                dfs("Basic Scripting")
                
        if skill not in resolved:
            resolved.append(skill)
            
    for skill in work_list:
        dfs(skill)
        
    return resolved

def get_role_details(interest, role_name):
    """
    Returns the core skills required for a specific role inside an interest zone.
    """
    return INTEREST_ROLES.get(interest, {}).get(role_name, [])

def get_top_roles(interest):
    """
    Returns the top 3 roles for a specific interest zone.
    """
    return list(INTEREST_ROLES.get(interest, {}).keys())[:3]
