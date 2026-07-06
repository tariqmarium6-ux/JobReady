# 🚀 JobReady AI
### AI-Powered Career Learning Platform for Emerging Technology Careers

> **JobReady AI** is an AI-assisted career learning platform that helps learners navigate rapidly evolving technology careers through curated, industry-aligned learning roadmaps. Instead of overwhelming users with thousands of unrelated courses, JobReady organizes learning into structured weekly pathways inspired by industry expectations.

---
Why JobReady?
Learning modern technology is no longer limited by the lack of content—it is limited by the lack of direction. JobReady was created to organize fragmented educational resources into structured, career-oriented roadmaps while using AI to support learners throughout their journey. Our goal is not to replace learning platforms, but to make learning paths clearer, more reliable, and easier to follow.

---
# 📖 Table of Contents

- Overview
- Problem Statement
- Solution
- Features
- Architecture
- AI Components
- Technology Stack
- Project Structure
- Installation
- Running Locally
- Deployment
- Screenshots
- Future Work
- Team

---

# 🎯 Problem Statement

Technology is evolving faster than ever, but learning platforms often leave users asking:

- Which technology should I learn?
- Which career roles exist within a domain?
- What should I study first?
- Which resources are trustworthy?
- What happens when recommended resources become unavailable?
- How can I stay organized throughout my learning journey?

Most platforms provide courses but not structured career roadmaps.

Learners often spend more time searching for resources than actually learning.

---

# 💡 Solution

JobReady transforms career exploration into a guided learning experience.

Instead of presenting thousands of disconnected resources, JobReady offers carefully curated learning pathways that take learners from career selection to structured weekly learning plans.

The platform combines:

- Career Domain Explorer
- Role Selection
- Weekly Learning Roadmaps
- Curated Educational Resources
- AI Study Assistant
- Progress Tracking
- Quiz System
- Resource Validation
- Automatic Resource Recovery

into a single modern learning platform.

---

# ✨ Key Features

## 🧭 Technology Domain Explorer

Explore high-demand technology domains including:

- Artificial Intelligence
- Agentic AI
- Machine Learning
- Data Science
- Cybersecurity
- Cloud Computing
- DevOps
- Software Engineering

Each domain contains multiple curated career roles.

---

## 🎓 Curated Career Roadmaps

Each role contains:

- Weekly learning timeline
- Learning objectives
- Industry competencies
- Recommended projects
- Trusted learning resources

The curriculum is professionally structured instead of randomly generated.

---

## 🤖 AI Study Assistant

Built using **Google Agent Development Kit (ADK)**.

Provides contextual assistance for the learner's current roadmap, helping explain concepts, recommend study strategies, and answer learning questions.

---

## 🔗 Intelligent Resource Validation

Educational resources frequently become unavailable over time.

JobReady automatically:

- detects broken resources
- validates educational links
- replaces unavailable resources with verified alternatives
- maintains an updated learning experience

---

## 📊 Learner Dashboard

Track:

- Weekly progress
- Study hours
- Course completion
- Learning timeline
- Weekly checklists

---

## 🧠 Knowledge Assessments

Generate quizzes to reinforce learning and evaluate weekly progress.

---

## 🏅 Achievement System

Learners earn badges based on:

- Study consistency
- Quiz performance
- Weekly completion

---

# 🏗 System Architecture

```text
                    +-------------------+
                    |   Technology      |
                    | Domain Explorer   |
                    +-------------------+
                              |
                              ▼
                    +-------------------+
                    |   Career Roles    |
                    +-------------------+
                              |
                              ▼
                    +-------------------+
                    | Weekly Curriculum |
                    +-------------------+
                              |
         +--------------------+--------------------+
         |                    |                    |
         ▼                    ▼                    ▼
  Curated Resources     AI Study Assistant   Progress Tracker
         |                    |                    |
         +--------------------+--------------------+
                              |
                              ▼
                    Resource Validator
                              |
                              ▼
                      Fallback Generator
```

---

# 🤖 AI Components

## 1. Study Assistant Agent

Built using:

- Google Agent Development Kit (ADK)
- Gemini

Responsibilities:

- Answer learner questions
- Explain concepts
- Support weekly learning

---

## 2. AI Fallback Helper

When educational resources become unavailable:

- Detects broken links
- Uses AI to recommend high-quality replacements
- Preserves learning continuity

---

# 🛠 Technology Stack

## Frontend

- Streamlit
- Custom HTML/CSS
- Modern Dark UI

---

## Backend

- Python

---

## AI

- Google Agent Development Kit (ADK)
- Gemini
- Groq
- Antigravity

---

## Database

- SQLite
- Firestore (optional)
- JSON Knowledge Base

---

## Deployment

- Docker
- Google Cloud Run

---

# 📂 Project Structure

```text
JobReady/
│
├── app.py
├── Dockerfile
├── requirements.txt
├── database/
│   ├── domains.json
│   ├── roles.json
│   ├── curriculum.json
│   ├── resources.json
│   ├── skills_network.json
│   └── resource_status.json
│
├── src/
│   ├── agents_config.py
│   ├── quiz_generator.py
│   ├── resource_validator.py
│   ├── ai_fallback_helper.py
│   ├── skill_graph.py
│   ├── oauth_handler.py
│   └── database_interface.py
│
└── README.md
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/tariqmarium6-ux/JobReady.git

cd JobReady
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶ Running Locally

```bash
streamlit run app.py
```

---

# ☁ Deployment

JobReady is containerized using Docker and deployed on **Google Cloud Run**.

Deployment workflow:

1. Build Docker image
2. Push to Google Artifact Registry
3. Deploy to Cloud Run
4. Configure environment variables
5. Launch application

---

# 📸 Screenshots



### Landing Page

![Landing](docs/landing.png)

---

### Career Domain Explorer

![Domains](docs/domains.png)

---

### Learning Dashboard

![Dashboard](docs/dashboard.png)

---

### Weekly Roadmap



---

---

# 👥 Team

**Project:** JobReady AI

Developed by: 
-Marium Tariq
-Farzeen Fatima

---

# 📄 License

This project was developed for educational and hackathon purposes.
