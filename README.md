# 🚀 JobReady

## Presentation and Overview

**Job ready link**: [https://jobready-xkwpqzwvtwevbls8wqhclw.streamlit.app/](https://jobready-xkwpqzwvtwevbls8wqhclw.streamlit.app/)

Explore the complete architectural breakdown and overview of the JobReady system

**Video Overview:** [Listen to the NotebookLM System Breakdown](https://notebooklm.google.com/notebook/9df5b136-2a6c-47e0-9e0b-3b58aaec0cb7/artifact/16e3e9ce-4b83-4688-890a-80d70b6a42a1?utm_source=nlm_web_share&utm_medium=google_oo&utm_campaign=art_share_1&utm_content=&utm_smc=nlm_web_share_google_oo_art_share_1_)

**Walk through DEMO**: [https://youtu.be/2NG5ruSRNJ4?si=b5K0xprPlqqHoBBQ](https://youtu.be/2NG5ruSRNJ4?si=b5K0xprPlqqHoBBQ)

**Presentation**: [https://notebooklm.google.com/notebook/9df5b136-2a6c-47e0-9e0b-3b58aaec0cb7/artifact/3844f39d-bcab-4a8e-b1f3-846b97cd4b22?utm_source=nlm_web_share&utm_medium=google_oo&utm_campaign=art_share_1&utm_content=&utm_smc=nlm_web_share_google_oo_art_share_1](https://notebooklm.google.com/notebook/9df5b136-2a6c-47e0-9e0b-3b58aaec0cb7/artifact/3844f39d-bcab-4a8e-b1f3-846b97cd4b22?utm_source=nlm_web_share&utm_medium=google_oo&utm_campaign=art_share_1&utm_content=&utm_smc=nlm_web_share_google_oo_art_share_1)_

> **Organizing the World's Free Learning Resources into Structured Career Paths**

JobReady solves a critical problem: **the world has unlimited free, high-quality learning resources (DeepLearning.AI, Hugging Face, freeCodeCamp, YouTube, official documentation ), but they're completely scattered and unorganized.**

JobReady curates, organizes, and sequences these free resources into structured learning paths so learners can go from "confused about where to start" to "job-ready" in weeks, not months.

---

# 📌 The Real Problem Statement

**The Resource Paradox:**

The internet has **unlimited free, high-quality resources**:

- DeepLearning.AI short courses (free)

- Hugging Face Learn (free)

- freeCodeCamp (free)

- PyTorch official tutorials (free)

- TensorFlow documentation (free)

- YouTube channels (free)

- MIT OpenCourseWare (free)

- Stanford CS courses (free)

- Official documentation everywhere (free)

**But here's the crisis:** These resources are **completely scattered and unorganized.**

A beginner wanting to become an **AI Engineer** faces impossible questions:

- Which resource should I start with?

- What's the optimal sequence?

- After this course, what's next?

- Am I actually ready for a job?

- How do I know I'm not wasting time on the wrong resources?

**The Result:** Learners jump randomly between courses, watch 10 different tutorials without a coherent path, waste 6-12 months, and never feel truly "job-ready."

**JobReady solves this:** It takes all these free, scattered resources and organizes them into a **clear, structured, sequenced learning path** for 160+ specialized tech roles.

---

# 💡 The Solution

JobReady is a **curation and organization platform** that:

1. **Aggregates** free resources from trusted platforms (DeepLearning.AI, Hugging Face, freeCodeCamp, official docs, YouTube, universities)

1. **Organizes** them by role (AI Engineer, Data Scientist, DevOps Engineer, etc.)

1. **Sequences** them into a logical 4-week learning path

1. **Validates** that all resources are active and accessible

1. **Personalizes** the experience with an AI Study Assistant

1. **Ensures** learners know exactly what to do, when to do it, and when they're job-ready

Users can now:

- Browse 210+ specialized tech roles

- See the exact learning path for each role

- Follow a structured 4-week curriculum

- Access validated, free resources in the right sequence

- Chat with an AI Study Assistant for help

- Track progress and know when they're job-ready

---

# ✨ Features

## 🎯 Technology Domain Explorer

- Browse 20 tech domains (AI, Data Science, Cloud, DevOps, Frontend, Backend, etc.)

- Premium dark UI with modern card layouts

- Search functionality

- Organized by industry demand and career potential

---

## 👨‍💻 Career Role Browser

Each domain contains 160+ specialized roles including:

- AI Engineer

- Machine Learning Engineer

- Prompt Engineer

- LLM Engineer

- Data Scientist

- DevOps Engineer

- Cloud Architect

- Full Stack Developer

- and many more...

Each role includes:

- Estimated learning duration (4 weeks)

- Difficulty level

- Industry outlook and job market demand

- Complete 4-week learning modules

---

## 📚 Weekly Learning Dashboard

Each learning path contains:

- Weekly learning objectives

- Curated, sequenced learning resources (all free)

- Learning checklist

- Progress tracking

- Study hour logging

- Certification upon completion

---

## 🤖 AI Study Assistant

JobReady integrates **Google Agent Development Kit (ADK)** to power an intelligent AI Study Assistant that:

- Understands your current role and week of learning

- Answers curriculum-related questions in real-time

- Explains difficult concepts in simple terms

- Provides encouragement and study tips

- Keeps you motivated throughout your learning journey

- Acts as a personal tutor available 24/7

---

## ✅ Resource Validation System

Broken educational resources destroy the learning experience.

JobReady includes an intelligent resource validation system that:

- Automatically checks if all resources are active and accessible

- Detects broken links before learners encounter them

- Swaps broken resources with verified alternatives

- Prioritizes official documentation and trusted platforms

- Ensures learners never waste time on dead links

---

## 🌙 Premium UI/UX

The interface was designed with inspiration from:

- Linear

- Coursera

- Stripe

- Vercel

Features include:

- Premium dark theme

- Modern glassmorphism

- Responsive layouts

- Consistent typography

- Accent-based color system

- Interactive cards

- Timeline-based learning dashboard

---

# 🧠 AI Features Deep Dive

JobReady uses intelligent AI agents to create a seamless, personalized learning experience:

## 1. Study Assistant Agent

**What it does:** An intelligent AI tutor powered by Google ADK and Gemini 1.5 Flash, embedded directly in the learning dashboard.

**Capabilities:**

- **Context-Aware Responses**: Understands your current role, week, and learning objectives

- **Concept Explanation**: Breaks down complex technical topics into simple, digestible explanations

- **Real-Time Guidance**: Answers curriculum-related questions instantly without going off-topic

- **Motivation & Support**: Provides encouragement and study tips to keep you engaged

- **Personalized Learning**: Tailors explanations based on your background and skill level

**Example Interaction:**

- You: "I don't understand backpropagation"

- Study Assistant: Explains the concept in simple terms with Python examples, then contextualizes it to your current learning path

- Result: You stay motivated and on track

---

## 2. Resource Validator

**What it does:** Automatically validates all learning resources in the curriculum to ensure they're active and accessible.

**How it works:**

- Performs HTTP health checks on all resource URLs

- Maintains a status cache to track resource availability

- Identifies broken links before you encounter them

- Swaps broken resources with verified fallbacks from a pre-curated registry

- Logs all changes for transparency

**Key Features:**

- **Parallel Validation**: Checks multiple links simultaneously for speed

- **Smart Fallback Matching**: Selects replacement resources based on skill category and learning objectives

- **Verified Resource Registry**: Prioritizes resources from trusted platforms (freeCodeCamp, HuggingFace, official documentation, universities, etc.)

- **Zero Dead Links**: You never encounter broken or unavailable resources

---

## 3. AI Fallback Helper

**What it does:** When all pre-curated fallbacks are exhausted, this agent uses Gemini to intelligently generate emergency replacement resources.

**How it works:**

- Analyzes the topic, learning objectives, and difficulty level

- Queries Gemini to generate a high-quality replacement resource

- Recommends stable, verified URLs from top-tier providers (MIT OpenCourseWare, Python Docs, PostgreSQL Tutorial, Docker Docs, etc.)

- Caches the generated resource to avoid redundant API calls

- Maintains a changelog for transparency

**Why it matters:**

- Ensures learning continuity even if multiple resources become unavailable

- Guarantees you always have access to quality content

- Reduces manual maintenance overhead

- Scales intelligently as the platform grows

**Example:**

- Original: "Advanced PyTorch Tutorial" (broken)

- Fallback 1: "PyTorch Official Tutorials" (also broken)

- Fallback 2: "freeCodeCamp PyTorch Course" (also broken)

- AI Fallback Helper: Generates "Python Docs - PyTorch API Reference" as emergency replacement

- Result: You continue learning without interruption

---

# 🚀 Key Innovation

JobReady's competitive advantage lies in its unique approach to **organizing free resources into structured career paths**:

## 1. Comprehensive Hardcoded Curriculum Database

- **160+ Specialized Roles**: Covering AI, Data Science, Cloud, DevOps, Frontend, Backend, and more

- **559KB of Structured Content**: A carefully curated, version-controlled curriculum database

- **4-Week Learning Paths**: Each role includes a complete 4-week learning journey with weekly objectives and resources

- **All Free Resources**: Aggregated from DeepLearning.AI, Hugging Face, freeCodeCamp, PyTorch, TensorFlow, Stanford, MIT, Harvard, NVIDIA, Google, Microsoft, and official documentation

- **Skill Dependencies**: Intelligent skill graph ensures prerequisites are taught before advanced topics

- **Sequenced Learning**: Resources are ordered logically so you know exactly what to do each week

## 2. Intelligent Resource Management

- **Automatic Validation**: Continuous health checks ensure resources remain accessible

- **Smart Fallback System**: Multi-tier fallback strategy (pre-curated → database → AI-generated)

- **Zero Broken Links**: You never encounter dead resources

- **Transparent Changelog**: All resource changes are logged and traceable

- **Quality Assurance**: Every resource is verified before being added to the curriculum

## 3. AI-Powered Personalization

- **Study Assistant Agent**: Real-time, context-aware AI tutor

- **Google ADK Integration**: Enterprise-grade agent orchestration

- **Gemini 1.5 Flash**: Fast, reliable, cost-effective LLM inference

- **Scalable Architecture**: Handles thousands of concurrent learners with personalized experiences

---

# 🏗 Architecture

```
                User

                  │

        Streamlit Frontend

                  │

        Learner Dashboard UI

                  │

 ┌─────────────────────────────────┐
 │                                 │
 │  Google ADK Study Assistant      │
 │  (Gemini 1.5 Flash)              │
 │                                 │
 └─────────────────────────────────┘

                  │

      Resource Validation Layer

      (URL Validator + AI Fallback Helper)

                  │

       Curated JSON Databases

        • Domains (20 tech domains)
        • Roles (160+ specialized roles)
        • Curriculum (559KB hardcoded)
        • Resources (33+ verified providers)
        • Skills Network (prerequisite graph)

                  │

      SQLite User Persistence
```

---

# 🛠 Technologies Used

## Frontend

- Streamlit

- HTML/CSS

- Custom CSS Styling

## Backend

- Python

## AI

- Google Agent Development Kit (ADK)

- Google Gemini 1.5 Flash

## Database

- SQLite

- JSON

## Deployment

- Streamlit Cloud

---

# 📂 Project Structure

```
JobReady/

├── database/
│   ├── curriculum.json          (559KB hardcoded curriculum)
│   ├── domains.json             (20 tech domains)
│   ├── resources.json           (33+ verified resource providers)
│   ├── roles.json               (160+ specialized roles)
│   ├── skills_network.json      (skill dependencies & prerequisites)
│   └── user_profiles.db         (SQLite user data)
│
├── src/
│   ├── app.py                   (Main Streamlit application)
│   ├── agents_config.py         (Google ADK agent configuration)
│   ├── resource_validator.py    (URL validation & fallback system)
│   ├── ai_fallback_helper.py    (AI-powered emergency resources)
│   ├── oauth_handler.py         (Authentication)
│   └── ...
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/tariqmarium6-ux/JobReady.git
```

Enter the project directory:

```bash
cd JobReady
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file containing:

```
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
```

Run the application:

```bash
streamlit run src/app.py
```

---

# ☁ Deployment

The application is containerized using Docker and deployed on **Streamlit Cloud**.

---

# 📸 Screenshots

- [Home Screen](https://github.com/tariqmarium6-ux/JobReady/blob/plan/skillbridge-ai/homescreen.png)

- [Domain Browser](https://github.com/tariqmarium6-ux/JobReady/blob/plan/skillbridge-ai/domain.png)

- [Career Role Selection](https://github.com/tariqmarium6-ux/JobReady/blob/plan/skillbridge-ai/careerrole.png)

- [Learner Dashboard](https://github.com/tariqmarium6-ux/JobReady/blob/plan/skillbridge-ai/dashboard.png)

- [AI Study Assistant](https://github.com/tariqmarium6-ux/JobReady/blob/plan/skillbridge-ai/assistant.png)

---

# 🎯 Future Improvements

- Personalized skill assessment based on resume

- Dynamic curriculum generation

- Live job market integration

- Certifications & achievements

- Community learning and peer support

- Resume-based role recommendations

---

# 👥 Authors

**Marium Tariq**

---

# 📄 License

This project is intended for educational and hackathon purposes.
