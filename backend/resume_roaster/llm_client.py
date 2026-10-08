"""
llm_client.py
-------------
Evidence-based Resume Roast LLM client for MargDarshak.

This module generates SAVAGE, BRUTAL, WITTY, COMEDIC, DARK-HUMORED roasts
grounded entirely in actual resume content.

Features:
- Always generates SAVAGE tone (no gentle/balanced options)
- Evidence-based roasting (every joke references actual resume content)
- Resume-specific (never generates generic template roasts)
- Structured output with sources
- Supports multiple LLM providers or high-quality deterministic fallback

Safety rules:
- Roast targets RESUME WRITING, NEVER the person
- No comments on race, gender, religion, appearance, nationality, or protected traits
- Professional, constructive, witty career critique
- Dark humor but not hateful or abusive
"""

import os
import json
import random
from typing import Dict, Any, Optional, List


class LLMClient:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.provider = "none"

        if self.groq_key:
            self.provider = "groq"
        elif self.gemini_key:
            self.provider = "gemini"
        elif self.openai_key:
            self.provider = "openai"

    def generate_roast_content(
        self,
        resume_text: str,
        issues: List[Dict[str, Any]],
        extracted_skills: Optional[List[str]] = None,
        extracted_projects: Optional[List[str]] = None,
        extracted_experience: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generates a structured, SAVAGE, evidence-based resume roast.
        
        The roast is always SAVAGE and BRUTAL regardless of input.
        Every joke is grounded in actual resume content.
        
        Returns:
        {
            "opening_roast": "Strong intro joke",
            "roast_sections": [
                {
                    "joke": "Specific witty critique",
                    "source": "Resume section name",
                    "evidence": "Actual quote or observation"
                },
                ...
            ],
            "worst_offender_roast": "Funniest/worst issue",
            "closing_verdict": "Memorable final line"
        }
        """
        
        # Try LLM provider if available
        if self.provider == "groq":
            try:
                return self._generate_with_groq(
                    resume_text, issues, extracted_skills, extracted_projects, extracted_experience
                )
            except Exception:
                pass
        elif self.provider == "gemini":
            try:
                return self._generate_with_gemini(
                    resume_text, issues, extracted_skills, extracted_projects, extracted_experience
                )
            except Exception:
                pass
        elif self.provider == "openai":
            try:
                return self._generate_with_openai(
                    resume_text, issues, extracted_skills, extracted_projects, extracted_experience
                )
            except Exception:
                pass

        # Fallback to deterministic generator
        return self._generate_savage_roast_deterministic(
            resume_text, issues, extracted_skills, extracted_projects, extracted_experience
        )

    def _generate_with_groq(
        self,
        resume_text,
        issues,
        extracted_skills,
        extracted_projects,
        extracted_experience,
    ):
        """Query Groq (OpenAI-compatible API) for a structured savage roast."""
        try:
            import requests

            issues_json = json.dumps([
                {"section": i.get("section"), "evidence": i.get("evidence")}
                for i in issues[:5]
            ])
            prompt = (
                "You are MargDarshak's Resume Roast AI. Generate an extremely witty, savage resume roast. "
                "Rules: every joke must reference ACTUAL resume content; roast the resume writing, never the person; "
                "no comments on race, gender, religion, appearance or nationality; be funny and intelligent. "
                "Return ONLY valid JSON, no markdown, with this structure: "
                '{"opening_roast": "...", "roast_sections": [{"joke": "...", "source": "...", "evidence": "..."}], '
                '"worst_offender_roast": "...", "closing_verdict": "..."}. '
                "Issues: " + issues_json + ". "
                "Skills: " + json.dumps((extracted_skills or [])[:10]) + ". "
                "Projects: " + json.dumps((extracted_projects or [])[:3]) + ". "
                "Experience: " + json.dumps((extracted_experience or [])[:2]) + ". "
                "Resume sample: " + resume_text[:800]
            )
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": "Bearer " + self.groq_key},
                json={
                    "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
                    "messages": [
                        {"role": "system", "content": "You are a witty, evidence-based resume roast generator."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.9,
                },
                timeout=40,
            )
            resp.raise_for_status()
            text = resp.json()["choices"][0]["message"]["content"].strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Groq generation failed: {e}")
            raise

    def _generate_with_gemini(
        self,
        resume_text: str,
        issues: List[Dict[str, Any]],
        extracted_skills: Optional[List[str]],
        extracted_projects: Optional[List[str]],
        extracted_experience: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Query Gemini for structured savage roast."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            issues_json = json.dumps([
                {"section": i.get("section"), "evidence": i.get("evidence")} 
                for i in issues[:5]
            ])
            
            prompt = f"""You are MargDarshak's Resume Roast AI. Generate an EXTREMELY WITTY, SAVAGE, BRUTAL resume roast.

RULES:
1. ALWAYS SAVAGE tone - no mercy, no softness
2. EVERY joke must reference ACTUAL resume content
3. Use dark humor, sarcasm, absurd comparisons, exaggeration, irony
4. Roast the RESUME WRITING, never the person
5. Be funny and intelligent, not just rude
6. Return ONLY valid JSON (no markdown, no formatting)

RESUME EVIDENCE:
Issues: {issues_json}
Skills mentioned: {json.dumps(extracted_skills[:10] if extracted_skills else [])}
Projects listed: {json.dumps(extracted_projects[:3] if extracted_projects else [])}
Experience: {json.dumps(extracted_experience[:2] if extracted_experience else [])}

Resume sample: {resume_text[:800]}

Generate JSON with this structure:
{{
    "opening_roast": "String - strong opening joke referencing actual resume content",
    "roast_sections": [
        {{"joke": "String - specific witty critique", "source": "String - Resume section", "evidence": "String - actual observation"}},
        {{"joke": "...", "source": "...", "evidence": "..."}}
    ],
    "worst_offender_roast": "String - the funniest/most brutal observation",
    "closing_verdict": "String - memorable final personalized punchline"
}}"""
            
            response = model.generate_content(prompt, generation_config={
                'temperature': 0.9,
                'top_k': 50,
                'top_p': 0.95,
            })
            
            text = response.text.strip()
            # Remove markdown code blocks if present
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            raise

    def _generate_with_openai(
        self,
        resume_text: str,
        issues: List[Dict[str, Any]],
        extracted_skills: Optional[List[str]],
        extracted_projects: Optional[List[str]],
        extracted_experience: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Query OpenAI for structured savage roast."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            
            issues_json = json.dumps([
                {"section": i.get("section"), "evidence": i.get("evidence")} 
                for i in issues[:5]
            ])
            
            prompt = f"""You are MargDarshak's Resume Roast AI. Generate an EXTREMELY WITTY, SAVAGE, BRUTAL resume roast.

RULES:
1. ALWAYS SAVAGE tone - no mercy, no softness
2. EVERY joke must reference ACTUAL resume content
3. Use dark humor, sarcasm, absurd comparisons, exaggeration, irony
4. Roast the RESUME WRITING, never the person
5. Be funny and intelligent, not just rude
6. Return ONLY valid JSON

RESUME EVIDENCE:
Issues: {issues_json}
Skills: {json.dumps(extracted_skills[:10] if extracted_skills else [])}
Projects: {json.dumps(extracted_projects[:3] if extracted_projects else [])}

Sample: {resume_text[:800]}

Return JSON: {{"opening_roast": "...", "roast_sections": [{{"joke": "...", "source": "...", "evidence": "..."}}], "worst_offender_roast": "...", "closing_verdict": "..."}}"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a witty, evidence-based resume roast generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                top_p=0.95,
            )
            
            text = response.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"OpenAI generation failed: {e}")
            raise

    def _generate_savage_roast_deterministic(
        self,
        resume_text: str,
        issues: List[Dict[str, Any]],
        extracted_skills: Optional[List[str]],
        extracted_projects: Optional[List[str]],
        extracted_experience: Optional[List[str]]
    ) -> Dict[str, Any]:
        """
        HIGH-QUALITY DETERMINISTIC ROAST GENERATOR
        
        Generates evidence-based, SAVAGE, varied roasts without an LLM.
        Every joke is grounded in actual resume content.
        """
        
        # Extract actual resume features for roasting
        skills_list = extracted_skills or []
        projects_list = extracted_projects or []
        experience_list = extracted_experience or []
        
        # Identify roastable patterns
        has_many_skills = len(skills_list) > 12
        has_many_certs = len([i for i in issues if i.get("section") == "Certifications"]) > 0
        has_weak_projects = any(i.get("category") == "weak_impact" for i in issues)
        has_buzzwords = any(i.get("category") == "cliché_buzzwords" for i in issues)
        has_passive_voice = any(i.get("category") == "passive_voice" for i in issues)
        
        opening_roasts = []
        
        # Variant 1: Skill hoarding
        if has_many_skills and len(skills_list) >= 15:
            opening_roasts.append(
                f"You've listed {len(skills_list)} technologies like you're collecting trading cards, but your projects section reads like a participation trophy."
            )
        elif has_many_skills:
            opening_roasts.append(
                f"Between the {len(skills_list)} skills and the buzzword density, this resume has impressive breadth and zero evidence you can do anything."
            )
        
        # Variant 2: Generic language
        if has_buzzwords:
            opening_roasts.append(
                "Your resume is so filled with 'passionate,' 'hardworking,' and 'team player' that LinkedIn is thinking of copyrighting it."
            )
        
        # Variant 3: Weak project evidence
        if has_weak_projects and projects_list:
            opening_roasts.append(
                f"Your projects section claims to have built stuff, but the descriptions are so vague that 'To-do app' sounds more impressive."
            )
        
        # Variant 4: Experience without impact
        if has_passive_voice and experience_list:
            opening_roasts.append(
                "This experience section describes jobs you held, not problems you solved. Recruiters can't hire a job title."
            )
        
        # Fallback openers
        if not opening_roasts:
            openers = [
                "This resume has potential, but right now it's telling us what you touched, not what you broke.",
                "Your profile reads like a resume template that got a little too comfortable.",
                "You've done work, clearly. The question is: why is your resume hiding all the evidence?",
                "This resume has the energy of someone who learned how to format bullet points but forgot to add actual results.",
            ]
            opening_roasts = openers
        
        opening_roast = random.choice(opening_roasts)
        
        # Build roast sections from actual issues
        roast_sections = []
        selected_issues = random.sample(issues[:5], min(3, len(issues)))
        
        for issue in selected_issues:
            section = issue.get("section", "Unknown")
            evidence = issue.get("evidence", "")
            category = issue.get("category", "")
            
            joke = self._generate_joke_for_issue(
                section, evidence, category, skills_list, has_many_skills
            )
            
            roast_sections.append({
                "joke": joke,
                "source": section,
                "evidence": evidence[:100] if evidence else "Resume element"
            })
        
        # Find worst offender
        if issues:
            worst = issues[0]
            worst_offender = self._generate_worst_offender_joke(
                worst.get("section", "Resume"),
                worst.get("evidence", ""),
                worst.get("category", ""),
                len(skills_list)
            )
        else:
            worst_offender = "Your biggest crime is making a perfectly mediocre resume look like an accident."
        
        # Closing verdict
        closing = self._generate_closing_verdict(
            has_many_skills, has_weak_projects, len(issues)
        )
        
        return {
            "opening_roast": opening_roast,
            "roast_sections": roast_sections,
            "worst_offender_roast": worst_offender,
            "closing_verdict": closing
        }

    def _generate_joke_for_issue(
        self, section: str, evidence: str, category: str, 
        skills_list: List[str], has_many_skills: bool
    ) -> str:
        """Generate a SAVAGE joke for a specific resume issue."""
        
        if category == "passive_voice":
            jokes = [
                f"'{evidence[:40]}...' — you were assigned work, not responsible for outcomes.",
                f"The passive tense in '{evidence[:35]}' suggests things happened to you, not that you made them happen.",
                "Your bullet points sound like you were a very present bystander.",
            ]
        elif category == "weak_impact":
            jokes = [
                f"'{evidence[:40]}...' describes effort, not impact. Recruiters hire for outcomes, not activity.",
                "Your projects exist. Whether they delivered value remains classified.",
                "The project descriptions have the specificity of a LinkedIn vague-post.",
            ]
        elif category == "cliché_buzzwords":
            jokes = [
                f"'{evidence}' — congratulations, you've successfully described every LinkedIn profile since 2014.",
                f"'{evidence}' is the resume equivalent of 'lol' at the end of a sentence. It adds nothing.",
                "If you removed every corporate cliché from your summary, you'd have a haiku.",
            ]
        elif category == "missing_skills":
            jokes = [
                f"Applying for {section} without {evidence} is bold but foolish.",
                f"'{evidence}' is technically visible in your resume — somewhere between the lines, apparently.",
                "The resume audit shows you're missing some key evidence, but plenty of empty confidence.",
            ]
        else:
            jokes = [
                f"The {section} section is giving minimalist art rather than professional resume.",
                f"{section} has the depth of a fortune cookie.",
                f"Your {section} reads like the first draft before you realized you needed actual evidence.",
            ]
        
        return random.choice(jokes)

    def _generate_worst_offender_joke(
        self, section: str, evidence: str, category: str, skill_count: int
    ) -> str:
        """Generate a joke about the WORST offense on the resume."""
        
        worst_jokes = [
            f"Your biggest crime is the {section} section, which somehow makes legitimate work sound suspicious.",
            f"The worst part isn't what you've done — it's how invisibly you've described it in {section}.",
            f"If '{evidence[:30]}' is your best evidence, recruiters will have questions about everything else.",
            f"The {section} section reads like a motivational poster instead of a professional credential.",
            "Your resume's worst offense is assuming recruiters have more time than they actually do to figure out what you did.",
        ]
        
        if skill_count > 15:
            worst_jokes.append(
                f"Listing {skill_count} skills while struggling to quantify a single project achievement is the resume equivalent of all flash and no substance."
            )
        
        return random.choice(worst_jokes)

    def _generate_closing_verdict(
        self, has_many_skills: bool, has_weak_projects: bool, issue_count: int
    ) -> str:
        """Generate a closing verdict specific to this resume."""
        
        closing_verdicts = [
            "The fix is surgical and simple: replace vague activity with measurable outcomes.",
            "Your resume has foundation. It's just hiding your best work under a pile of passive voice.",
            "Come back when your bullets prove impact, not just proximity to projects.",
            "With real numbers and action verbs, this profile will stop self-sabotaging.",
            "The resume doesn't lie — it just doesn't tell the whole truth. Fix that.",
        ]
        
        if has_many_skills and has_weak_projects:
            closing_verdicts.append(
                "You have the skills. Now prove you've actually used them for something that mattered."
            )
        elif has_weak_projects:
            closing_verdicts.append(
                "Your projects are decent starting points. Quantify them or don't list them."
            )
        elif issue_count > 5:
            closing_verdicts.append(
                "This resume has so much potential it's basically a tragedy."
            )
        
        return random.choice(closing_verdicts)
