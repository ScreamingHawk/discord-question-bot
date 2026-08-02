import json
from pathlib import Path

SAFE_FIRST = [
    "live beside the sea", "live in the mountains", "start a new career at forty", "retire earlier on less money",
    "speak every language", "master one musical instrument", "travel slowly for a year", "settle permanently near family",
    "work four long days each week", "take a three-month sabbatical", "own a small home outright", "rent a beautiful home anywhere",
    "host every social gathering", "attend without ever hosting", "know exactly what others think of you", "never worry what others think",
    "relive one excellent year", "skip one difficult year ahead", "keep every photograph you have taken", "keep every message you have received",
    "have a private chef", "have a weekly housekeeper", "be recognised everywhere for your work", "be wealthy and completely anonymous",
    "always arrive thirty minutes early",
]
SAFE_SECOND = [
    "have twice as much free time", "have a guaranteed meaningful job", "move to a country you have never visited",
    "stay in your current community for life", "give up social media permanently", "give up streaming entertainment permanently",
    "have an extra day every week", "receive one honest answer to any question", "be excellent at every hobby you try",
    "always know when someone is being sincere",
]
NSFW_FIRST = [
    "share a long-held fantasy with a partner", "receive a naked massage", "give a naked massage", "have sex with the lights fully on",
    "have sex in complete darkness", "use a sex toy together", "try consensual role-play", "send an explicit voice message",
    "receive an explicit voice message", "spend an hour on foreplay", "skip straight to your favourite sexual act",
    "take control in bed", "let your partner take control in bed", "be watched by a consenting partner while you touch yourself",
    "watch a consenting partner touch themselves", "try something new in a private hotel room", "have slow morning sex",
    "have energetic late-night sex", "talk openly about every turn-on", "reveal your biggest turn-off", "be blindfolded by someone you trust",
    "blindfold someone who trusts you", "choose the music during sex", "let your partner choose the mood for the night",
    "spend the night focused entirely on kissing and touching",
]
NSFW_SECOND = [
    "act out a mutually agreed fantasy", "buy a new toy together", "have an explicit conversation before touching",
    "let anticipation build all day", "focus entirely on giving pleasure", "focus entirely on receiving pleasure",
    "try a new position chosen together", "share erotic stories with each other", "have a playful quickie",
    "plan a long intimate night with no interruptions",
]


def build(first, second):
    return [f"Would you rather {left}, or {right}?" for left in first for right in second]


output = Path(__file__).parents[1] / "src/question_bot/data/would_you_rather.json"
output.write_text(json.dumps({"safe": build(SAFE_FIRST, SAFE_SECOND), "nsfw": build(NSFW_FIRST, NSFW_SECOND)}, indent=2) + "\n")
