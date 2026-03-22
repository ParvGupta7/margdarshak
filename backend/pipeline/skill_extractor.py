"""
skill_extractor.py
------------------
PIPELINE STEP 4: Skill Extraction

Maps resume tokens against the master skills database using exact matching only.

Method: Exact substring match with word boundary enforcement.
  - Handles multi-word skills (e.g., "machine learning", "natural language processing")
    by matching against the full cleaned text string.
  - Uses regex word boundaries (\b) to prevent partial matches
    (e.g., "r" should not match "rest api").
  - Case-insensitive matching on lowercased text.

Fuzzy matching was intentionally removed — it introduced too many false positives
for short technical skill names (e.g., "go" fuzzy-matching "r", "c" matching "c++").
Exact matching on a comprehensive 500+ skill database is more reliable.
"""

import re
from data.skills_db import SKILLS_DB


def extract_skills(clean_text: str, tokens: list) -> dict:
    """
    Entry point for Step 4.

    Args:
        clean_text: Whitespace-normalized, lowercased text from preprocessor stage 4
        tokens: Lemmatized token list from preprocessor stage 7 (used for token count only)

    Returns:
        dict with matched skills, category breakdown, and match details
    """
    matched = {}

    for category, skills in SKILLS_DB.items():
        for skill in skills:
            skill_lower = skill.lower()
            # Word boundary regex prevents partial matches
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, clean_text):
                matched[skill] = {
                    "method": "exact",
                    "category": category
                }

    # Organize by category
    by_category = {}
    for skill, info in matched.items():
        cat = info["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(skill)

    return {
        "matched_skills": list(matched.keys()),
        "skill_count": len(matched),
        "by_category": by_category,
        "match_details": matched
    }
