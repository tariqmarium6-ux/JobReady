# 🚀 JobReady

#  Presentation and Overview

**Job ready link**: https://jobready-xkwpqzwvtwevbls8wqhclw.streamlit.app/

Explore the complete architectural breakdown and overview of the JobReady system
**video Overview:** [Listen to the NotebookLM System Breakdown](https://notebooklm.google.com/notebook/9df5b136-2a6c-47e0-9e0b-3b58aaec0cb7/artifact/16e3e9ce-4b83-4688-890a-80d70b6a42a1?utm_source=nlm_web_share&utm_medium=google_oo&utm_campaign=art_share_1&utm_content=&utm_smc=nlm_web_share_google_oo_art_share_1_)

**presentation**: https://notebooklm.google.com/notebook/9df5b136-2a6c-47e0-9e0b-3b58aaec0cb7/artifact/3844f39d-bcab-4a8e-b1f3-846b97cd4b22?utm_source=nlm_web_share&utm_medium=google_oo&utm_campaign=art_share_1&utm_content=&utm_smc=nlm_web_share_google_oo_art_share_1_

> **Curated AI & Tech Learning Paths for Career Readiness**

JobReady is an AI-powered learning platform that helps aspiring developers and technology enthusiasts discover structured learning paths for high-demand careers in Artificial Intelligence and emerging technologies.

Unlike generic search engines or scattered tutorials, JobReady provides carefully curated learning journeys inspired by platforms like Coursera, DeepLearning.AI, Hugging Face, and official documentation. Every learning path is organized into weekly modules with trusted resources, allowing learners to focus on learning instead of spending hours searching for quality content.

---

# 📌 Problem Statement

Learning AI and modern technology is overwhelming.

A beginner often faces questions like:

* Which technology should I learn first?
* Which role matches my interests?
* Which resources are actually trustworthy?
* How do I organize hundreds of tutorials into a structured learning path?

Most learners jump between YouTube videos, blogs, documentation, and online courses without a clear roadmap. This leads to information overload and low completion rates.

JobReady solves this by providing curated, structured, career-oriented learning paths.

---

# 💡 Solution

JobReady offers a guided learning experience where users can:

* Browse high-demand technology domains.
* Explore multiple career roles inside each domain.
* Follow structured weekly learning modules.
* Access carefully validated learning resources.
* Track learning progress.
* Chat with an integrated AI Study Assistant for learning support.

The platform focuses on simplicity, premium UI, and curated quality rather than overwhelming users with endless search results.

---

# ✨ Features

## 🎯 Technology Domain Explorer

* Browse multiple AI and technology domains.
* Premium dark UI with modern card layouts.
* Search supported.
* Technology organized into curated categories.

---

## 👨‍💻 Career Role Browser

Each domain contains multiple career roles including:

* AI Engineer
* Machine Learning Engineer
* Prompt Engineer
* LLM Engineer
* Data Scientist
* DevOps Engineer
and more 160 roles

Each role includes:

* Estimated learning duration
* Difficulty
* Industry outlook
* Learning modules

---

## 📚 Weekly Learning Dashboard

Each learning path contains:

* Weekly objectives
* Curated learning resources
* Learning checklist
* Progress tracking
* Study hour logging

---

## 🤖 AI Study Assistant

JobReady integrates **Google Agent Development Kit (ADK)** to power an AI Study Assistant that helps learners:

* Understand difficult concepts
* Answer curriculum-related questions
* Stay motivated
* Clarify weekly learning objectives

The assistant acts as an intelligent tutor throughout the learning journey.

---

## ✅ Resource Validation System

Broken educational resources can ruin the learning experience.

JobReady includes a resource validation system that:

* Detects unavailable learning resources
* Uses verified fallback resources
* Prioritizes official documentation and trusted platforms
* Prevents learners from encountering dead links

---

## 🌙 Premium UI/UX

The interface was redesigned with inspiration from:

* Linear
* Coursera
* Stripe
* Vercel

Features include:

* Premium dark theme
* Modern glassmorphism
* Responsive layouts
* Consistent typography
* Accent-based color system
* Interactive cards
* Timeline-based learning dashboard

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
 │                                 │
 └─────────────────────────────────┘

                  │

      Resource Validation Layer

                  │

       Curated JSON Databases

        • Domains
        • Roles
        • Curriculum
        • Resources
        • Skills Network

                  │

      SQLite User Persistence
```

---

# 🛠 Technologies Used

## Frontend

* Streamlit
* HTML/CSS
* Custom CSS Styling

## Backend

* Python

## AI

* Google Agent Development Kit (ADK)
* Google Gemini 1.5 Flash

## Database

* SQLite
* JSON

## Deployment

* Docker
* Google Cloud Run

---

# 📂 Project Structure

```
JobReady/

├── database/
│   ├── curriculum.json
│   ├── domains.json
│   ├── resources.json
│   ├── roles.json
│   ├── skills_network.json
│   └── user_profiles.db
│
├── src/
│   ├── app.py
│   ├── agents_config.py
│   ├── resource_validator.py
│   ├── ai_fallback_helper.py
│   ├── oauth_handler.py
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

```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
```

Run the application:

```bash
streamlit run src/app.py
```

---

# ☁ Deployment

The application is containerized using Docker and deployed on **Google Cloud Run**.

Deployment workflow:

1. Build Docker image
2. Push container
3. Deploy to Cloud Run
4. Configure environment variables
5. Launch application

---

# 📸 Screenshots


* [Home Screen](homescreen.png)
* [Domain Browser](domain.png)
* [Career Role Selection](careerrole.png)
* [Learner Dashboard](dashboard.png)
* [AI Study Assistant](assistant.png)
---

# 🎯 Future Improvements

* Personalized skill assessment
* Dynamic curriculum generation
* Live job market integration
* Certifications & achievements
* Community learning
* Resume-based recommendations

---

# 👥 Authors

**Marium Tariq**
**Farzeen Fatima**

Developed for the Kaggle X Google capstone project

---

# 📄 License

This project is intended for educational and hackathon purposes.
