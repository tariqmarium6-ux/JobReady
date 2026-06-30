import json
import os

ROLES_FILE = "database/roles.json"

CAPSTONES = {
    "Penetration Tester": {
        "title": "Enterprise Active Directory Exploitation and Hardening Lab",
        "problem_statement": "An enterprise client needs a security audit of their multi-domain Active Directory forest containing legacy protocols, misconfigured service accounts, and unpatched domain controllers.",
        "expected_deliverables": [
            "Comprehensive Penetration Testing Report with executive summary and technical walkthroughs",
            "Remediation guidelines and PowerShell hardening scripts",
            "BloodHound network attack path graphs"
        ],
        "deployment_recommendation": "Local VMware ESXi or AWS VPC lab environment",
        "github_repository": "enterprise-ad-audit",
        "readme_requirements": [
            "Lab topology diagram",
            "Tools used and attack commands reference",
            "Remediation verification log"
        ],
        "suggested_resume_bullet": "Executed a mock security audit of an enterprise Active Directory domain, identifying 4 critical path vulnerabilities including Kerberoasting and AS-REP roasting.",
        "suggested_linkedin_project_description": "Designed and executed an enterprise AD penetration test simulating modern threat actor methodologies. Conducted post-compromise reconnaissance using BloodHound and implemented GPO hardening configurations."
    },
    "Machine Learning Engineer": {
        "title": "Distributed Transformer Fine-Tuning Pipeline",
        "problem_statement": "Build a scalable, distributed pipeline to fine-tune an open-source Large Language Model (e.g. Llama-3-8B) on domain-specific medical conversation datasets.",
        "expected_deliverables": [
            "PyTorch DDP training script with DeepSpeed integration",
            "WandB dashboard showing loss curves and memory utilization metrics",
            "quantized GGUF model files ready for edge CPU deployment"
        ],
        "deployment_recommendation": "RunPod or AWS EC2 with multi-GPU setup",
        "github_repository": "distributed-transformer-tuner",
        "readme_requirements": [
            "Dataset preprocessing flow diagram",
            "Multi-node launch instructions",
            "Hardware performance benchmarks"
        ],
        "suggested_resume_bullet": "Developed a distributed PyTorch LLM fine-tuning pipeline using DeepSpeed ZeRO-3, reducing training time by 40% on multi-GPU nodes.",
        "suggested_linkedin_project_description": "Engineered a production-ready distributed training pipeline for fine-tuning open-source LLMs. Optimized training memory footprints using LoRA and 8-bit quantization techniques."
    },
    "Cloud Solutions Architect": {
        "title": "Multi-Region Multi-Tenant SaaS Infrastructure",
        "problem_statement": "Design a highly available, fault-tolerant, and secure multi-tenant infrastructure on AWS to support a global B2B SaaS application with strict compliance needs.",
        "expected_deliverables": [
            "Terraform code defining the VPC, ECS/EKS clusters, and RDS Aurora Global databases",
            "IAM least-privilege security policies",
            "Cost optimization report detailing AWS Savings Plans"
        ],
        "deployment_recommendation": "AWS (Amazon Web Services)",
        "github_repository": "multi-region-tenant-saas",
        "readme_requirements": [
            "Architectural design diagram using AWS icons",
            "Terraform apply instructions and variables guide",
            "Failover verification test procedures"
        ],
        "suggested_resume_bullet": "Designed and deployed a Terraform-based multi-region SaaS infrastructure on AWS utilizing ECS and RDS Aurora, achieving 99.99% availability.",
        "suggested_linkedin_project_description": "Created a production-ready Terraform blueprint for a multi-tenant cloud application. Integrated AWS KMS for database encryption and implemented auto-scaling profiles matching traffic peaks."
    },
    "Full Stack Developer": {
        "title": "Real-Time Collaborative Document Workspace",
        "problem_statement": "Build a collaborative workspace platform (similar to Notion/Google Docs) allowing multiple concurrent users to edit documents with real-time cursor tracking and comments.",
        "expected_deliverables": [
            "React frontend utilizing block-based editors (EditorJS) and Yjs CRDTs",
            "Node.js/WebSockets server managing document sync state",
            "OAuth integration (Google/GitHub) and PostgreSQL database storage"
        ],
        "deployment_recommendation": "Vercel + Render + Supabase",
        "github_repository": "collaborative-doc-workspace",
        "readme_requirements": [
            "WebSockets sync architecture diagram",
            "Local environment setup guide",
            "CRDT conflict resolution explanation"
        ],
        "suggested_resume_bullet": "Engineered a real-time collaborative document editor using React and WebSockets, supporting 50+ concurrent users with sub-50ms conflict resolution.",
        "suggested_linkedin_project_description": "Built a collaborative rich-text editor from scratch using CRDTs (Conflict-free Replicated Data Types) for real-time document synchronization. Integrated WebSockets for bi-directional messaging."
    },
    "Data Scientist": {
        "title": "Predictive Customer Lifetime Value (CLV) Platform",
        "problem_statement": "Develop an end-to-end predictive analytics system that forecasts customer lifetime value and churn probability using historical transactions.",
        "expected_deliverables": [
            "Jupyter Notebook containing EDA and feature engineering pipelines",
            "Trained XGBoost model with hyperparameter tuning metadata",
            "REST API delivering live prediction outputs from inputs"
        ],
        "deployment_recommendation": "Heroku or AWS Lambda",
        "github_repository": "predictive-clv-platform",
        "readme_requirements": [
            "Feature importance breakdown graphs",
            "Model metrics summary (ROC-AUC, Precision/Recall)",
            "API endpoint request/response docs"
        ],
        "suggested_resume_bullet": "Developed a predictive Customer Lifetime Value model using XGBoost, improving target marketing campaign efficiency by 22%.",
        "suggested_linkedin_project_description": "Built a machine learning platform to forecast user churn and CLV. Implemented cohort analysis, RFM segmentation, and integrated predictions into a web endpoint."
    },
    "DevOps Engineer": {
        "title": "GitOps-Driven Kubernetes CI/CD Engine",
        "problem_statement": "Architect a secure, automated software delivery pipeline that automatically builds, tests, and deploys applications to a Kubernetes cluster upon code commit.",
        "expected_deliverables": [
            "GitHub Actions workflow compiling Docker images and running tests",
            "ArgoCD application manifests implementing continuous deployment syncs",
            "Sops-encrypted Kubernetes secrets configurations"
        ],
        "deployment_recommendation": "GitHub Actions + ArgoCD + Minikube/EKS",
        "github_repository": "gitops-k8s-cicd",
        "readme_requirements": [
            "CI/CD workflow flowchart",
            "ArgoCD deployment guide",
            "Secrets management and decryption guide"
        ],
        "suggested_resume_bullet": "Implemented a GitOps deployment pipeline using ArgoCD and GitHub Actions on Kubernetes, reducing manual releases to zero.",
        "suggested_linkedin_project_description": "Created a declarative GitOps engine for cloud-native microservices. Automated container builds, security scans, and sync tasks using ArgoCD."
    },
    "Data Pipeline Engineer": {
        "title": "Real-Time IoT Event Streaming and Analytics Pipeline",
        "problem_statement": "Build an ingestion pipeline that handles high-throughput IoT sensor data streams, processes them in real-time, and stores them in a data warehouse for analytics.",
        "expected_deliverables": [
            "Dockerized Kafka clusters managing ingestion topics",
            "Apache Spark streaming code performing window aggregations",
            "PostgreSQL/TimescaleDB time-series storage schema"
        ],
        "deployment_recommendation": "Docker Compose or Confluent Cloud + Databricks",
        "github_repository": "iot-streaming-pipeline",
        "readme_requirements": [
            "Data flow diagram",
            "Throughput benchmarks and scalability metrics",
            "Grafana dashboard monitoring config"
        ],
        "suggested_resume_bullet": "Architected a real-time event streaming pipeline processing 10,000+ messages/sec using Apache Kafka and Spark Streaming.",
        "suggested_linkedin_project_description": "Engineered a highly available data ingestion pipeline for IoT time-series metrics. Optimized Spark partition counts and consumer offsets to guarantee zero data loss."
    },
    "Frontend Engineer": {
        "title": "High-Performance SaaS Enterprise Dashboard",
        "problem_statement": "Develop a state-of-the-art enterprise admin dashboard with advanced data grid filters, chart visualizations, and high accessibility metrics.",
        "expected_deliverables": [
            "Next.js app built with React, TypeScript, and TailwindCSS",
            "Custom component library featuring accessible design tokens",
            "Lighthouse audits showing 100/100 performance scores"
        ],
        "deployment_recommendation": "Vercel",
        "github_repository": "enterprise-saas-dashboard",
        "readme_requirements": [
            "Component tree structure overview",
            "State management logic walkthrough",
            "Performance optimization documentation"
        ],
        "suggested_resume_bullet": "Built a responsive React SaaS dashboard with Next.js, achieving sub-second page loads and 100/100 Lighthouse performance metrics.",
        "suggested_linkedin_project_description": "Developed an accessible, highly optimized SaaS dashboard. Implemented bundle splitting, component memoization, and complex chart renders."
    },
    "Backend Engineer": {
        "title": "Scalable Microservices API Gateway and Auth Server",
        "problem_statement": "Design a high-throughput, secure API Gateway that manages token-based authentication, request routing, and rate-limiting for backend microservices.",
        "expected_deliverables": [
            "FastAPI Gateway router handling JWT authentication",
            "Redis backend cache implementing token bucket rate-limiting",
            "Docker configurations containerizing each service micro-app"
        ],
        "deployment_recommendation": "AWS ECS or local Docker swarm",
        "github_repository": "scalable-api-gateway",
        "readme_requirements": [
            "Microservices connectivity diagram",
            "Auth flow handshake sequences",
            "Stress test results using Locust"
        ],
        "suggested_resume_bullet": "Designed a FastAPI API Gateway with JWT auth and Redis rate-limiting, managing 1.5M+ daily requests with 99.9% uptime.",
        "suggested_linkedin_project_description": "Engineered a secure microservices router featuring Redis-based token buckets and stateless JWT authentication checks. Conducted load tests under concurrent peaks."
    },
    "UI/UX Designer": {
        "title": "Design System and High-Fidelity Telehealth App Prototype",
        "problem_statement": "Design a mobile telehealth application focused on elderly accessibility, ensuring simple appointment scheduling and drug tracking layouts.",
        "expected_deliverables": [
            "Figma design system with dynamic tokens, auto-layouts, and dark mode variants",
            "Interactive high-fidelity clickable prototype of the appointment flows",
            "UX research report detailing user interviews and accessibility audit"
        ],
        "deployment_recommendation": "Figma Community link",
        "github_repository": "telehealth-accessibility-system",
        "readme_requirements": [
            "User persona breakdowns",
            "UI Kit components library preview",
            "Accessibility guidelines (WCAG 2.1 AA) compliance check"
        ],
        "suggested_resume_bullet": "Created a Figma telehealth design system containing 40+ reusable components, enhancing design team layout speed by 35%.",
        "suggested_linkedin_project_description": "Led UX research and interface design for an accessibility-first telehealth platform. Conducted usability testing sessions and built a responsive UI component kit."
    }
}

def inject():
    if not os.path.exists(ROLES_FILE):
        print("[ERROR]: roles.json not found.")
        return
        
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        roles_db = json.load(f)
        
    count = 0
    for role_name, capstone in CAPSTONES.items():
        if role_name in roles_db:
            roles_db[role_name]["standardized_capstone"] = capstone
            count += 1
            
    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(roles_db, f, indent=2)
        
    print(f"[SUCCESS]: Injected high-quality standardized_capstones into {count} flagship roles.")

if __name__ == "__main__":
    inject()
