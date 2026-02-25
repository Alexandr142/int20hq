MODEL = "llama"

INTENTS = ["payment_issue", "technical_issue", "account_access", "tariff_refund"]

CASE_TYPES = ["success", "fail", "conflict", "agent_mistake", "hidden_unsatisfaction"]

PERSONALITIES = [
    {
        "type": "elderly/non-tech",
        "traits": "doesn't understand technical terms, frequent typos, requires detailed explanation."
    },
    {
        "type": "polite",
        "traits": "writes politely, less typos."
    },
    {
        "type": "quick-tempered",
        "traits": "wants issue to be solved immediately otherwise starts conflict, when aggressive more typos and might"
                  "write in capslock."
    },
]

AGENT_MISTAKES = ["ignored_question", "incorrect_info", "rude_tone", "no_resolution", "unnecessary_escalation"]
