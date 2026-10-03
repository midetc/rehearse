import json
from pathlib import Path

CATALOG_DIR = Path(__file__).resolve().parent / "catalog_data"

ICON_LABELS = {
    "python-developer": "Py",
    "java-developer": "Jv",
    "devops": "Ops",
    "ai-engineer": "AI",
    "qa": "QA",
    "data-analyst": "DA",
    "cpp-robotics": "C++",
    "rust": "Rs",
    "kotlin": "Kt",
    "go": "Go",
}

TRACK_ORDER = [
    "python-developer",
    "java-developer",
    "go",
    "rust",
    "cpp-robotics",
    "kotlin",
    "devops",
    "ai-engineer",
    "qa",
    "data-analyst",
]


def uniquify_questions(item):
    seen = set()
    categories = []
    for cat in item["categories"]:
        cards = []
        for index, card in enumerate(cat["cards"], start=1):
            question = card["question"].strip()
            if question in seen:
                question = f"{question} ({cat['name']} #{index})"
            seen.add(question)
            cards.append({**card, "question": question})
        categories.append({**cat, "cards": cards})
    return {**item, "categories": categories}


def load_track(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    data = uniquify_questions(data)
    data["icon"] = ICON_LABELS.get(data["slug"], data["slug"][:2].title())
    return data


def load_catalog():
    by_slug = {
        path.stem: load_track(path)
        for path in CATALOG_DIR.glob("*.json")
    }
    ordered = [by_slug[slug] for slug in TRACK_ORDER if slug in by_slug]
    extras = [
        by_slug[slug]
        for slug in sorted(by_slug)
        if slug not in TRACK_ORDER
    ]
    return ordered + extras


CATALOG = load_catalog()
