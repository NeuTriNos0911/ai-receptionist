import json
import os
from pathlib import Path
from typing import Any


DEFAULT_PROFILE = {
    "business_name": "Universal AI Call Centre",
    "industry": "local service business",
    "market": "India",
    "language": "English",
    "accent": "friendly local Indian English accent",
    "tone": "warm, clear, professional, and concise",
    "opening": "Hello, thanks for calling. How can I help you today?",
    "summary": "An AI receptionist that can answer common questions, capture leads, and request a human callback.",
    "services": [
        {
            "name": "Customer support",
            "details": "Answer common questions, collect customer details, and explain next steps."
        },
        {
            "name": "Appointments and callbacks",
            "details": "Collect the caller's name, phone number, reason for calling, and preferred time."
        }
    ],
    "faqs": [
        {
            "question": "Can I speak to a human?",
            "answer": "Yes. I can collect your details and arrange a callback from the team."
        }
    ],
    "handoff_rules": [
        "The caller asks for payment, legal, medical, or emergency advice.",
        "The caller is angry or says the issue is urgent.",
        "The agent is unsure about the answer."
    ],
    "fallback": "I do not have that exact detail yet, but I can take your information and ask the team to call you back."
}


def load_business_profile() -> dict[str, Any]:
    profile_path = Path(os.getenv("BUSINESS_PROFILE_PATH", "business_profile.json"))
    if not profile_path.is_absolute():
        profile_path = Path(__file__).resolve().parent / profile_path

    if not profile_path.exists():
        return DEFAULT_PROFILE

    with profile_path.open("r", encoding="utf-8") as profile_file:
        profile = json.load(profile_file)

    return {**DEFAULT_PROFILE, **profile}


def format_business_knowledge(profile: dict[str, Any]) -> str:
    services = "\n".join(
        f"- {item.get('name', 'Service')}: {item.get('details', '')}"
        for item in profile.get("services", [])
    )
    faqs = "\n".join(
        f"- Q: {item.get('question', '')}\n  A: {item.get('answer', '')}"
        for item in profile.get("faqs", [])
    )
    handoff_rules = "\n".join(f"- {rule}" for rule in profile.get("handoff_rules", []))

    return f"""
Business name: {profile.get("business_name")}
Industry: {profile.get("industry")}
Market: {profile.get("market")}
Summary: {profile.get("summary")}

Services:
{services or "- No services configured yet."}

FAQs:
{faqs or "- No FAQs configured yet."}

Handoff rules:
{handoff_rules or "- Use judgment when a human should call back."}

Fallback answer:
{profile.get("fallback")}
"""


def search_profile(profile: dict[str, Any], topic: str) -> str:
    topic_terms = [term.lower() for term in topic.split() if len(term) > 2]
    matches: list[str] = []

    for service in profile.get("services", []):
        text = f"{service.get('name', '')} {service.get('details', '')}"
        if any(term in text.lower() for term in topic_terms):
            matches.append(f"{service.get('name')}: {service.get('details')}")

    for faq in profile.get("faqs", []):
        text = f"{faq.get('question', '')} {faq.get('answer', '')}"
        if any(term in text.lower() for term in topic_terms):
            matches.append(f"Q: {faq.get('question')}\nA: {faq.get('answer')}")

    if matches:
        return "\n\n".join(matches[:5])

    return format_business_knowledge(profile)
