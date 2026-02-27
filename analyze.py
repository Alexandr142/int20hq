import json
import argparse
import ollama
from tqdm import tqdm
import re

MODEL = "qwen3:8b"

ANALYSIS_PROMPT_TEMPLATE = """
You are an expert QA auditor evaluating customer support chats.
Return ONLY a valid JSON object.

DO NOT guess policies.
DO NOT invent mistakes.
ONLY describe what is directly observable.

CATEGORIES:
- request_intent: "payment problems", "technical errors", "account access", "questions about the tariff", "refund", "other"
- customer_satisfaction: "satisfied", "neutral", "unsatisfied"
- agent_mistakes: ONLY from:
  - no_resolution
  - rude_tone
  - ignored_question

DIALOGUE:
{dialogue_text}

OUTPUT JSON:
{{
  "reasoning": "1 sentence max",
  "request_intent": "string",
  "customer_satisfaction": "string",
  "agent_mistakes": ["string"]
}}
"""

INTENT_MAP = {
    "refund": "refund",
    "tariff_refund": "refund",
    "tariff": "questions about the tariff",
    "questions about the tariff": "questions about the tariff",

    "payment problems": "payment problems",
    "payment issue": "payment problems",

    "technical errors": "technical errors",
    "technical issue": "technical errors",

    "account access": "account access",
}

SATISFACTION_MAP = {
    "satisfied": "satisfied",
    "neutral": "neutral",
    "unsatisfied": "unsatisfied",
    "dissatisfied": "unsatisfied",
}

CONFIDENCE_WEAK_PHRASES = [
    "should be fixed",
    "might work",
    "try again",
    "hopefully",
    "possible",
    "we'll see"
]

def format_chat(chat):
    return "\n".join(
        f"[{m.get('role','').upper()}]: {m.get('text','')}"
        for m in chat
    )

def analyze_dialogue(chat):
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(
        dialogue_text=format_chat(chat)
    )

    try:
        response = ollama.generate(
            model=MODEL,
            prompt=prompt,
            options={"temperature": 0.0, "seed": 42}
        )

        text = re.sub(r"<think>.*?</think>", "", response["response"], flags=re.S)
        text = text.replace("```json", "").replace("```", "").strip()

        match = re.search(r"\{.*\}", text, re.S)
        return json.loads(match.group()) if match else {}

    except Exception:
        return {}

def normalize_labels(r):
    r["request_intent"] = INTENT_MAP.get(
        r.get("request_intent", "").lower().strip(), "other"
    )
    r["customer_satisfaction"] = SATISFACTION_MAP.get(
        r.get("customer_satisfaction", "").lower().strip(), "unsatisfied"
    )
    r["agent_mistakes"] = list(set(r.get("agent_mistakes", [])))
    return r

def infer_no_resolution(chat, result):
    last_agent = next(
        (m["text"].lower() for m in reversed(chat) if m["role"] == "agent"),
        ""
    )

    unresolved = (
        result["customer_satisfaction"] != "satisfied"
        or any(p in last_agent for p in CONFIDENCE_WEAK_PHRASES)
        or "escalate" in last_agent
    )

    if unresolved and "no_resolution" not in result["agent_mistakes"]:
        result["agent_mistakes"].append("no_resolution")

def clamp_satisfaction(result):
    if "no_resolution" in result["agent_mistakes"]:
        result["customer_satisfaction"] = "unsatisfied"

def recompute_quality_score(result):
    mistakes = set(result["agent_mistakes"])

    if "rude_tone" in mistakes:
        return 1

    if "no_resolution" in mistakes:
        return 2

    if mistakes:
        return 4

    return 5

def final_validation(result):
    if result["request_intent"] not in INTENT_MAP.values():
        result["request_intent"] = "other"

    if result["customer_satisfaction"] not in SATISFACTION_MAP.values():
        result["customer_satisfaction"] = "unsatisfied"

    if result["customer_satisfaction"] == "unsatisfied":
        result["quality_score"] = min(result["quality_score"], 2)

    result["quality_score"] = max(1, min(5, result["quality_score"]))
    return result

def run_analysis(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in tqdm(data):
        chat = item.get("chat", [])
        r = analyze_dialogue(chat)

        r = normalize_labels(r)
        infer_no_resolution(chat, r)
        clamp_satisfaction(r)

        r["quality_score"] = recompute_quality_score(r)
        r = final_validation(r)

        item["analysis"] = r

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✔ Analysis complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/dataset.json")
    parser.add_argument("--output", default="data/evaluated_test.json")
    args = parser.parse_args()

    run_analysis(args.input, args.output)