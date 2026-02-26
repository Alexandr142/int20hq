import json
from collections import Counter

INPUT_FILE = "data/evaluated_test.json"
TOP_N_MISMATCHES = 15

INTENT_GT_TO_PRED = {
    "payment_issue": "payment problems",
    "technical_issue": "technical errors",
    "account_access": "account access",
    "tariff_refund": "refund",
}

UNSAT_CASE_TYPES = {
    "fail", "conflict", "problematic",
    "hidden_unsatisfaction", "agent_mistake"
}

def expected_satisfaction(case_type: str) -> str:
    return "satisfied" if case_type == "success" else "unsatisfied"

def expected_score_range(case_type: str):
    if case_type == "success":
        return 4, 5
    if case_type == "conflict":
        return 2, 3
    return 1, 2

def normalize(text: str) -> str:
    return (text or "").strip().lower()

def has_no_resolution(agent_mistakes):
    return "no_resolution" in set(agent_mistakes or [])

def print_confusion_matrix(cm, labels, title):
    print(f"\n=== {title} (Confusion Matrix) ===")
    header = ["GT\\PRED"] + labels
    width = max(len(x) for x in header) + 2

    print("".join(h.ljust(width) for h in header))
    for gt in labels:
        row = [gt] + [str(cm[(gt, pr)]) for pr in labels]
        print("".join(x.ljust(width) for x in row))

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    n = len(data)
    if n == 0:
        print("Dataset is empty.")
        return

    intent_correct = 0
    satisfaction_correct = 0
    no_resolution_correct = 0
    score_correct = 0

    intent_labels = list(INTENT_GT_TO_PRED.values()) + ["other"]
    intent_cm = Counter()
    satisfaction_cm = Counter()

    mismatches = []

    for item in data:
        _id = item.get("id")
        meta = item.get("metadata", {})
        pred = item.get("analysis", {})

        # ---------- Ground truth ----------
        gt_intent = INTENT_GT_TO_PRED.get(
            normalize(meta.get("intent")), "other"
        )
        gt_case = normalize(meta.get("case_type"))
        gt_satisfaction = expected_satisfaction(gt_case)
        gt_no_resolution = gt_case != "success"
        score_lo, score_hi = expected_score_range(gt_case)

        # ---------- Prediction ----------
        pr_intent = normalize(pred.get("request_intent"))
        pr_intent = {
            "payment issue": "payment problems",
            "technical issue": "technical errors",
            "login issue": "account access",
            "tariff": "questions about the tariff",
        }.get(pr_intent, pr_intent)

        if pr_intent not in intent_labels:
            pr_intent = "other"

        pr_satisfaction = normalize(pred.get("customer_satisfaction"))
        if pr_satisfaction not in {"satisfied", "unsatisfied", "neutral"}:
            pr_satisfaction = "unsatisfied"

        pr_mistakes = pred.get("agent_mistakes", [])
        pr_no_resolution = has_no_resolution(pr_mistakes)

        pr_score = pred.get("quality_score")

        # ---------- Intent ----------
        intent_cm[(gt_intent, pr_intent)] += 1
        if gt_intent == pr_intent:
            intent_correct += 1
        else:
            mismatches.append(
                (_id, "intent", gt_intent, pr_intent)
            )

        # ---------- Satisfaction ----------
        satisfaction_cm[(gt_satisfaction, pr_satisfaction)] += 1
        if gt_satisfaction == pr_satisfaction:
            satisfaction_correct += 1
        else:
            mismatches.append(
                (_id, "satisfaction", gt_satisfaction, pr_satisfaction)
            )

        # ---------- no_resolution ----------
        if gt_no_resolution == pr_no_resolution:
            no_resolution_correct += 1
        else:
            mismatches.append(
                (_id, "no_resolution", gt_no_resolution, pr_no_resolution)
            )

        # ---------- Quality score ----------
        if isinstance(pr_score, int) and score_lo <= pr_score <= score_hi:
            score_correct += 1
        else:
            mismatches.append(
                (_id, "quality_score", f"{score_lo}-{score_hi}", pr_score)
            )

    # ============================================================
    # Results
    # ============================================================

    print("\n==============================")
    print("LLM PERFORMANCE EVALUATION")
    print("==============================")
    print(f"Dialogs analyzed: {n}")

    print("\n--- Accuracy ---")
    print(f"Intent accuracy:        {intent_correct / n:.2%}")
    print(f"Satisfaction accuracy:  {satisfaction_correct / n:.2%}")
    print(f"No-resolution accuracy: {no_resolution_correct / n:.2%}")
    print(f"Score-in-range:         {score_correct / n:.2%}")

    print_confusion_matrix(intent_cm, intent_labels, "Intent")
    print_confusion_matrix(
        satisfaction_cm,
        ["satisfied", "unsatisfied", "neutral"],
        "Satisfaction"
    )

    print(f"\n--- Top {TOP_N_MISMATCHES} mismatches ---")
    for m in mismatches[:TOP_N_MISMATCHES]:
        print(f"ID {m[0]} | {m[1]} | expected={m[2]} | got={m[3]}")

    print("\nDone.")

if __name__ == "__main__":
    main()