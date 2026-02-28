Ось фінальна, вилизана версія README.md англійською мовою. Вона враховує всі наші виправлення в Docker, структуру папок та особливості запуску.
🛡️ AI-Powered Customer Support QA & Dataset Generator

An advanced automated system designed to generate high-fidelity synthetic support dialogues and perform deep quality analysis using LLMs (Llama 3 via Ollama). This tool helps companies evaluate support agent performance at scale without manual auditing.
✨ Key Features
    + Persona-Driven Generation: Creates dialogues based on diverse customer profiles, from tech-savvy professionals to frustrated seniors.
    + Intent-Specific Scenarios: Covers critical support domains including payments, technical issues, account access, and refunds.
    + Behavioral Case Types: Generates successful, problematic, and conflict-driven interactions to test evaluation robustness.
    + Automated Mistake Injection: Specifically simulates 10+ types of agent errors such as ignored questions, rude tones, and incorrect information.
    + Robust Evaluation Engine: Automatically detects intents, calculates quality scores (1-5), and identifies hidden customer dissatisfaction.

🛠️ Installation & Setup
1. 🐋 Using Docker (Recommended)

The project is fully containerized. This command starts both the Python application and the Ollama LLM server.

# 1. Start the containers
docker-compose up -d --build

# 2. Download the Llama3 model into the container
docker exec -it ollama_service ollama pull llama3

2. 🛠 Manual Setup

If you prefer running locally:

# 1. Install dependencies
pip install -r requirements.txt

# 2. Ensure Ollama is installed on your OS and pull the model
ollama pull llama3

# 3. Start generation from the project root
python generate.py

💻 Usage

Our tool features a flexible CLI powered by argparse, allowing for both bulk generation and targeted edge-case testing.
Data Generation
Command	Description
python generate.py --samples 5	Generates a full balanced dataset (5 samples per case type).
python generate.py --intent payment_issue --samples 10	Targets specific payment-related issues.
python generate.py --mistake rude_tone --samples 5	Generates dialogues where the agent is specifically rude.
Dataset Analytics

Use our utility tool to check your data distribution:
Bash

# Run from the project root
python -m src.utils stats --input data/dataset.json

📊 Technical Specifications
Supported Intents

The system is pre-configured to handle:

    payment_issue: Billing, card rejection, double charges.

    technical_issue: App crashes, bugs, performance issues.

    account_access: 2FA problems, password resets.

    tariff_refund: Refund requests and plan cancellations.

Evaluation Metrics

The analyze.py script provides:

    Quality Score: A 1-5 rating based on professional support standards.

    Mistake Detection: Checks for specific errors like incorrect_info or lack_of_empathy.

    Intent Validation: Compares the LLM's perceived intent with the original metadata.

🏗️ Project Structure

project_root/
├── data/               # Generated JSON datasets
├── src/
│   ├── __init__.py     # Package marker
│   ├── config.py       # Definitions of intents, personas, and mistakes
│   ├── prompts.py      # LLM System prompts & special requirements
│   └── utils.py        # CLI tools for statistics and path handling
├── generate.py         # Main generation engine
├── analyze.py          # QA evaluation script
├── Dockerfile          # App container definition
└── docker-compose.yml  # Multi-container orchestration (App + Ollama)
