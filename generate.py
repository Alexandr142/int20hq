from src.utils import get_ollama_endpoint
from src.prompts import *
from src.config import *
from tqdm import tqdm
import argparse
import ollama
import random
import json
import re
import os


class ChatGenerator:
    def __init__(self, model=MODEL, filename="dataset.json"):
        self.endpoint = get_ollama_endpoint()
        self.client = ollama.Client(host=self.endpoint)
        self.model = model
        self.path = os.path.join("data", filename)
        self.current_id = 1
        self.dataset = []

    def _check_connection(self):
        """Verifies if Ollama is reachable and the model is pulled."""
        try:
            self.client.list()
            print(f"[+] Connected to Ollama at {self.endpoint}")
        except Exception as e:
            print(f"[!] Critical Error: Cannot connect to Ollama at {self.endpoint}")
            print(f"[!] Make sure Ollama is running and accessible.")
            exit(1)

    def _clean_json(self, raw_data):
        """Cleans JSON returned by a model."""
        match = re.search(r'(\{.*}|\[.*])', raw_data, re.DOTALL)
        return match.group(1) if match else raw_data

    def generate_single_chat(self, data_id, intent, case_type, personality, agent_mistake="none"):
        """Calls LLM for one chat generation."""
        prompt = CHAT_GENERATION_PROMPT.format(
            intent=intent,
            case_type=case_type,
            personality_type=personality["type"],
            personality_traits=personality["traits"],
            mistake=agent_mistake
        )
        prompt += SPECIAL_REQUIREMENTS.get(case_type, "")
        prompt += INTENT_REQUIREMENTS.get(intent, "")

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            format="json",
            options={"temperature": 0.7}
        )

        clean_json = self._clean_json(response["response"])
        messages = json.loads(clean_json)

        # Ignored question mistake handling
        messages = messages.get("messages", []) if agent_mistake != "ignored_question" else [messages]

        if len(messages) == 0:
            raise Exception("Generated empty chat")

        return {
            "id": data_id,
            "metadata": {
                "intent": intent,
                "case_type": case_type,
                "personality_type": personality["type"],
                "mistake": agent_mistake
            },
            "chat": messages
        }

    def save_data(self):
        """Saves current dataset into a file."""
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, indent=4, ensure_ascii=False)

    def load_dataset(self):
        """Load dataset from existing file"""
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.dataset = json.load(f)
                self.current_id = max((chat["id"] for chat in self.dataset)) + 1
                print(f"[*] Resuming from ID {self.current_id}")
            except Exception as e:
                print(f"[!] Could not read existing file: {e}")

    def generate_samples(self, n, case_type=None, intent=None, personality=None, mistake=None, checkpoint=5):
        """Generates specific samples or random in case of None"""
        for _ in tqdm(range(n)):
            case_type_ = case_type if case_type is not None else random.choice(CASE_TYPES)
            intent_ = intent if intent is not None else random.choice(INTENTS)
            personality_ = personality if personality is not None else random.choice(PERSONALITIES)
            mistake_ = (random.choice(AGENT_MISTAKES) if mistake is None else mistake)
            mistake_ = mistake_ if case_type_ == "agent_mistake" else "none"

            try:
                chat_data = self.generate_single_chat(self.current_id, intent_, case_type_, personality_, mistake_)
                self.dataset.append(chat_data)
                self.current_id += 1
            except Exception as e:
                print(f"[!] Error at ID {self.current_id}: {e}")
                continue

            # Checkpoint
            if checkpoint > 0 and self.current_id % checkpoint == 0:
                self.save_data()

    def run(self, samples_per_case=3, checkpoint=5):
        """Generator cycle."""
        self.load_dataset()

        print(f"[*] Starting generation with model: {self.model}")

        for case_type in CASE_TYPES:
            print(f"[*] Generating '{case_type}' cases...")
            self.generate_samples(samples_per_case, case_type, checkpoint=checkpoint)

        self.save_data()
        print(f"[+] Done! Saved {len(self.dataset)} chats to {self.path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Customer Support Chat Dataset Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Basic settings
    parser.add_argument("--file", type=str, default="dataset.json", help="Output file name")
    parser.add_argument("--samples", type=int, default=3,
                        help="Samples per case type (for run) or total (for specific generation)")
    parser.add_argument("--checkpoint", type=int, default=5, help="Save every N samples")
    parser.add_argument("--model", type=str, default=MODEL, help="Model name")

    # Specific generation overrides
    parser.add_argument("--intent", type=str, choices=INTENTS, help="Filter by specific intent")
    parser.add_argument("--case_type", type=str, choices=CASE_TYPES, help="Filter by specific case type")
    parser.add_argument("--mistake", type=str, choices=AGENT_MISTAKES, help="Filter by specific agent mistake")
    parser.add_argument("--personality", type=str, choices=[p["type"] for p in PERSONALITIES], help="Filter by personality type")

    args = parser.parse_args()

    # Initialize generator
    generator = ChatGenerator(model=args.model, filename=args.file)
    generator.load_dataset()

    if any([args.intent, args.case_type, args.mistake, args.personality]):
        print(f"[*] Target generation: intent={args.intent}, case={args.case_type}, mistake={args.mistake}, personality={args.personality}")

        personality = next((p for p in PERSONALITIES if p["type"] == args.personality), None)

        generator.generate_samples(
            n=args.samples,
            case_type=args.case_type,
            intent=args.intent,
            personality=args.personality,
            mistake=args.mistake,
            checkpoint=args.checkpoint
        )
        generator.save_data()
        print(f"[+] Specific generation complete. Saved to data/{args.file}")
    else:
        generator.run(
            samples_per_case=args.samples,
            checkpoint=args.checkpoint
        )
