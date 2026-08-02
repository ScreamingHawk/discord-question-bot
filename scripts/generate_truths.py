import json
from pathlib import Path

SUBJECTS = [
    "friendship", "family relationships", "romantic relationships", "career choices", "money",
    "health", "ageing", "personal values", "cultural identity", "home", "travel", "ambition",
    "failure", "success", "loneliness", "community", "trust", "forgiveness", "habits",
    "self-confidence", "work-life balance", "parenthood or choosing not to parent", "technology",
    "spirituality or meaning", "the future",
]
SAFE_TEMPLATES = [
    "What is the most honest thing you can say about {subject}?",
    "What have you changed your mind about when it comes to {subject}?",
    "What do you wish people understood about your experience with {subject}?",
    "What choice involving {subject} are you proudest of?",
    "What is one mistake about {subject} that taught you something valuable?",
    "What do you currently want more of when it comes to {subject}?",
    "What do you find hardest to admit about {subject}?",
    "What expectation around {subject} have you stopped trying to meet?",
    "What would your younger self be surprised to learn about your experience with {subject}?",
    "What boundary have you learned to set around {subject}?",
]
INTIMATE_SUBJECTS = [
    "sexual confidence", "your strongest turn-ons", "your biggest turn-offs", "a private fantasy",
    "communicating what you want during sex", "initiating sex", "flirting", "kissing", "foreplay",
    "aftercare", "sex toys", "role-play", "erotic media", "body confidence during sex", "nudity",
    "sexual boundaries", "giving and receiving consent", "monogamy or non-monogamy",
    "sexual compatibility", "the best sex you have had", "an awkward sexual moment",
    "trying something new in bed", "talking about sexual health", "differences in libido",
    "feeling desired",
]
NSFW_TEMPLATES = [
    "What is the most honest thing you can say about {subject}?",
    "What have you learned about yourself through {subject}?",
    "What do you wish a partner understood about you when it comes to {subject}?",
    "What is something about {subject} that you find difficult to ask for?",
    "What past experience most shaped how you feel about {subject}?",
    "What would make you feel safer and more relaxed around {subject}?",
    "What would you like to explore with a consenting adult involving {subject}?",
    "What boundary matters most to you when it comes to {subject}?",
    "What about {subject} has improved as you have grown older?",
    "What is a misconception people often have about {subject}?",
]


def build(templates, subjects):
    return [template.format(subject=subject) for template in templates for subject in subjects]


output = Path(__file__).parents[1] / "src/question_bot/data/truth.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({"safe": build(SAFE_TEMPLATES, SUBJECTS), "nsfw": build(NSFW_TEMPLATES, INTIMATE_SUBJECTS)}, indent=2) + "\n")
