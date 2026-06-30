---
name: extract-baseline
description: |
  Extracts and structures a user's current technical competencies from raw resume text or direct input. 
  Use when the user uploads a resume, pastes their background, or asks to identify their current skills.
  Do NOT use for matching roles or generating the curriculum.
version: 1.0.0
license: MIT
---

# Extract Baseline Skill

## When to use
Trigger this skill when a user provides their professional background, a list of technologies they know, or a raw resume text dump, and you need to establish their current technical stack[cite: 1].

## When NOT to use
Do not use this skill to figure out what skills the user needs to learn, or to search the internet for courses[cite: 1].

## Workflow
1. Read the provided user input or parsed resume text[cite: 1].
2. Identify all explicit programming languages, frameworks, tools, and methodologies mentioned.
3. Clean the list (e.g., group variant names like "ReactJS" and "React" together).
4. Output the final baseline as a structured JSON list of skills[cite: 1].

## Output format
Return ONLY a valid JSON array of strings representing the extracted skills.
Example: `["Python", "SQL", "TensorFlow", "Git"]`[cite: 1]