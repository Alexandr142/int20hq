MODEL = "llama3"

INTENTS = [
    "payment_issue",
    "technical_issue",
    "account_access",
    "tariff_refund"
]

CASE_TYPES = [
    "success",
    "fail",
    "conflict",
    "agent_mistake",
    "problematic",
    "hidden_unsatisfaction"
]

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
        "type": "senior",
        "traits": "confuses terms, needs simple steps, polite but slow."
    },
    {
        "type": "exec",
        "traits": "short sentences, expects speed, values time over small talk."
    },
    {
        "type": "detailer",
        "traits": "structured lists, technical accuracy, polite but demanding."
    },
    {
        "type": "mobile",
        "traits": "typos, abbreviations, delayed responses, multi-tasking."
    },
    {
        "type": "loyalist",
        "traits": "friendly, expects personal touch, mentions long history."
    },
    {
        "type": "skeptic",
        "traits": "already troubleshooting, asks deep questions, doubts basics."
    },
    {
        "type": "chaotic",
        "traits": "might use unusual slang and abbreviations."
    },
    {
        "type": "uneducated",
        "traits": "many spelling errors, grammatically incorrect sentences, swearing words."
    }
]

AGENT_MISTAKES = [
    "ignored_question",
    "incorrect_info",
    "rude_tone",
    "no_resolution",
    "unnecessary_escalation",
    "robotic_responses",
    "overly_complex_jargon",
    "premature_closing",
    "lack_of_empathy",
    "repeated_questions"
]
