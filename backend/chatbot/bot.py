"""
bot.py
------
PIPELINE STEP 9: Chatbot

A context-aware chatbot that:
  1. Holds the full resume analysis as its knowledge base
  2. Classifies user intent to route simple queries without calling the API
  3. Uses the Claude API (claude-haiku) for complex or general questions

Intent Classification (keyword-based — fast, no ML model needed):
  - COURSES: questions about learning, courses, skills to improve
  - JOBS: questions about job listings, applying, roles
  - SKILLS: questions about extracted skills, what was found
  - GAP: questions about missing skills, what to learn
  - PROFILE: questions about extracted resume info
  - GENERAL: everything else → sent to Claude API

The knowledge base is built from the complete analysis result and injected
into the system prompt so Claude has full context.
"""

import os
import anthropic
import json
from typing import Optional

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


# ---------- Intent Classification ----------

INTENT_PATTERNS = {
    "COURSES": [
        "course", "learn", "tutorial", "certification", "study",
        "training", "resource", "free", "platform", "coursera", "udemy"
    ],
    "JOBS": [
        "job", "jobs", "hiring", "opening", "vacancy", "apply",
        "company", "salary", "work", "position", "listing"
    ],
    "SKILLS": [
        "skill", "skills", "technology", "tools", "know", "extracted",
        "found", "have", "strong", "good at"
    ],
    "GAP": [
        "missing", "gap", "lack", "need", "improve", "should learn",
        "not have", "weak", "add", "acquire"
    ],
    "PROFILE": [
        "name", "email", "phone", "contact", "location", "linkedin",
        "profile", "information", "resume", "detail"
    ]
}


def classify_intent(user_message: str) -> str:
    """
    Keyword-based intent classification.
    Returns the most likely intent category.
    """
    message_lower = user_message.lower()
    scores = {intent: 0 for intent in INTENT_PATTERNS}

    for intent, keywords in INTENT_PATTERNS.items():
        for keyword in keywords:
            if keyword in message_lower:
                scores[intent] += 1

    best_intent = max(scores, key=scores.get)
    if scores[best_intent] == 0:
        return "GENERAL"
    return best_intent


# ---------- Quick-Answer Handlers (no API call needed) ----------

def handle_intent(intent: str, analysis: dict, user_message: str) -> Optional[str]:
    """
    Handles intents that can be answered directly from the analysis data
    without calling the Claude API.

    Returns a response string if handled, None if Claude API should be used.
    """
    if intent == "PROFILE":
        entities = analysis.get("entities", {})
        lines = ["Here is what was extracted from your resume:"]
        if entities.get("name"):
            lines.append(f"Name: {entities['name']}")
        if entities.get("email"):
            lines.append(f"Email: {entities['email']}")
        if entities.get("phone"):
            lines.append(f"Phone: {entities['phone']}")
        if entities.get("location"):
            lines.append(f"Location: {entities['location']}")
        if entities.get("linkedin"):
            lines.append(f"LinkedIn: {entities['linkedin']}")
        return "\n".join(lines)

    if intent == "SKILLS":
        skills = analysis.get("skills", {}).get("matched_skills", [])
        count = len(skills)
        if not skills:
            return "No skills were extracted from your resume. Make sure your resume clearly lists technologies and tools."
        sample = ", ".join(skills[:15])
        more = f" and {count - 15} more" if count > 15 else ""
        return f"I found {count} skills in your resume: {sample}{more}."

    if intent == "GAP":
        best_role = analysis.get("job_roles", {}).get("best_match", {})
        if not best_role:
            return "No job role analysis available yet."
        role_name = best_role.get("role", "")
        gaps = analysis.get("gaps", {}).get("gaps", {}).get(role_name, {})
        missing = gaps.get("missing_required", [])
        if not missing:
            return f"Great news — you have all the required skills for {role_name}!"
        return f"For {role_name}, you are missing these required skills: {', '.join(missing)}."

    return None  # Let Claude handle it


# ---------- Claude API Integration ----------

def build_system_prompt(analysis: dict) -> str:
    """
    Builds a detailed system prompt with the full analysis as context.
    Claude uses this as its knowledge base for the conversation.
    """
    entities = analysis.get("entities", {})
    skills = analysis.get("skills", {}).get("matched_skills", [])
    top_roles = analysis.get("job_roles", {}).get("top_roles", [])
    gaps = analysis.get("gaps", {}).get("gaps", {})

    best_role = top_roles[0]["role"] if top_roles else "Unknown"
    best_score = top_roles[0]["score"] if top_roles else 0

    roles_summary = "\n".join([
        f"  - {r['role']}: {r['score']}% match"
        for r in top_roles[:4]
    ])

    missing_for_best = gaps.get(best_role, {}).get("missing_required", [])

    context = f"""You are MargDarshak, an AI career guidance assistant. You have already analyzed this person's resume.

RESUME ANALYSIS SUMMARY:
- Name: {entities.get('name', 'Not found')}
- Location: {entities.get('location', 'Not found')}
- Skills found ({len(skills)} total): {', '.join(skills[:20])}{'...' if len(skills) > 20 else ''}
- Best job match: {best_role} ({best_score}% match)
- Top matches:
{roles_summary}
- Missing required skills for {best_role}: {', '.join(missing_for_best) if missing_for_best else 'None — fully qualified!'}

FULL GAPS DATA:
{json.dumps(gaps, indent=2)[:1500]}

INSTRUCTIONS:
- Be concise, direct, and helpful.
- Use the resume data above when answering questions.
- Give practical, actionable career advice.
- If asked about courses or resources, suggest free options first.
- Do not add unnecessary disclaimers.
- Address the person warmly but professionally.
- Respond in plain text, not markdown.
"""
    return context


def chat(user_message: str, analysis: dict, history: list) -> dict:
    """
    Main chat function. Classifies intent, handles simple queries directly,
    routes complex queries to Claude API.

    Args:
        user_message: User's input string
        analysis: Full resume analysis dict
        history: List of previous messages [{"role": "user/assistant", "content": "..."}]

    Returns:
        dict with response, intent, and method used
    """
    intent = classify_intent(user_message)

    # Try to handle without API call
    quick_response = handle_intent(intent, analysis, user_message)
    if quick_response and intent != "GENERAL":
        return {
            "response": quick_response,
            "intent": intent,
            "method": "local_handler"
        }

    # Fall back to Claude API
    if not ANTHROPIC_API_KEY:
        return {
            "response": "Chatbot is not configured. Add your ANTHROPIC_API_KEY to the .env file to enable AI-powered responses.",
            "intent": intent,
            "method": "error"
        }

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        system_prompt = build_system_prompt(analysis)

        # Build messages with history
        messages = []
        for msg in history[-10:]:  # Last 10 turns to stay within context limits
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=system_prompt,
            messages=messages
        )

        return {
            "response": response.content[0].text,
            "intent": intent,
            "method": "claude_api"
        }

    except Exception as e:
        return {
            "response": f"Unable to reach the AI assistant right now. Error: {str(e)}",
            "intent": intent,
            "method": "error"
        }
