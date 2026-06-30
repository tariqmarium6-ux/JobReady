from datetime import datetime

# Unique completion badges mapping
COMPLETION_BADGES = {
    "Data Scientist": "Insight Architect",
    "Machine Learning Engineer": "Model Forgemaster",
    "Frontend Engineer": "Interface Artisan",
    "Backend Engineer": "System Builder",
    "DevOps Engineer": "Deployment Commander",
    "Cloud Solutions Architect": "Cloud Navigator",
    "Cybersecurity Engineer": "Digital Sentinel",
    "Penetration Tester": "Red Team Operative",
    "UI/UX Designer": "Experience Designer",
    "Full Stack Developer": "Stack Virtuoso"
}

BADGE_DESCRIPTIONS = {
    "First Week Completed": "Completed your very first week on JobReady!",
    "7-Day Study Streak": "Kept your study fire burning for 7 consecutive days!",
    "Quiz Master": "Achieved a perfect 5/5 score on a weekly assessment quiz!",
    "Portfolio Builder": "Built at least 3 portfolio projects in your roadmaps!",
    "Consistency Award": "Completed 4 consecutive weeks of study!",
    "Fast Learner": "Completed a full curriculum roadmap at a high-intensity study pace!",
    
    # Completion Badges
    "Insight Architect": "Master of analytics, cohorts, and predictive data modeling.",
    "Model Forgemaster": "Master of deep networks, distributed tuners, and ML deployment pipelines.",
    "Interface Artisan": "Master of Next.js, responsive layouts, and modern SaaS UI dashboards.",
    "System Builder": "Master of FastAPI gateways, stateless JWT auth, and Redis rate limiters.",
    "Deployment Commander": "Master of Docker configurations, continuous GitOps, and ArgoCD engines.",
    "Cloud Navigator": "Master of multi-region high-availability SaaS infrastructure on AWS.",
    "Digital Sentinel": "Master of security architectures, vulnerability audits, and network defenses.",
    "Red Team Operative": "Master of Active Directory exploitation, BloodHound paths, and GPO hardening.",
    "Experience Designer": "Master of elderly accessibility, WCAG standards, and interactive Figma systems.",
    "Stack Virtuoso": "Master of collaborative rich-text editing and multi-user Websockets workspaces."
}

def evaluate_badges(google_id: str, role_name: str, total_weeks: int, db_provider) -> list:
    """Check user metrics against milestones and award new badges. Returns list of all badges."""
    profile = db_provider.get_user_profile(google_id)
    progress = db_provider.get_progress(google_id, role_name)
    
    completed_weeks = progress.get("completed_weeks", [])
    completed_projects = progress.get("completed_projects", [])
    
    newly_awarded = []
    
    # 1. First Week Completed
    if len(completed_weeks) >= 1:
        if db_provider.add_user_badge(google_id, "First Week Completed"):
            newly_awarded.append("First Week Completed")
            
    # 2. 7-Day Study Streak
    if profile.get("streak_count", 0) >= 7:
        if db_provider.add_user_badge(google_id, "7-Day Study Streak"):
            newly_awarded.append("7-Day Study Streak")
            
    # 3. Portfolio Builder (completed >= 3 projects)
    if len(completed_projects) >= 3:
        if db_provider.add_user_badge(google_id, "Portfolio Builder"):
            newly_awarded.append("Portfolio Builder")
            
    # 4. Consistency Award (completed >= 4 weeks)
    if len(completed_weeks) >= 4:
        if db_provider.add_user_badge(google_id, "Consistency Award"):
            newly_awarded.append("Consistency Award")
            
    # Check quiz score for Quiz Master
    # Let's check all quiz records for the user in this role
    has_perfect_quiz = False
    for wk_num in range(1, total_weeks + 1):
        quiz_rec = db_provider.get_quiz_record(google_id, role_name, wk_num)
        if quiz_rec.get("best_score", 0) == 5:
            has_perfect_quiz = True
            break
            
    if has_perfect_quiz:
        if db_provider.add_user_badge(google_id, "Quiz Master"):
            newly_awarded.append("Quiz Master")

    # 5. Fast Learner & Unique Completion Badge
    if len(completed_weeks) >= total_weeks and total_weeks > 0:
        # Check if they are a Fast Learner (Pace >= 35)
        if profile.get("study_pace", 15) >= 35:
            if db_provider.add_user_badge(google_id, "Fast Learner"):
                newly_awarded.append("Fast Learner")
                
        # Completion Badge
        comp_badge = COMPLETION_BADGES.get(role_name)
        if comp_badge:
            if db_provider.add_user_badge(google_id, comp_badge):
                newly_awarded.append(comp_badge)
                
    all_badges = db_provider.get_user_badges(google_id)
    return all_badges
