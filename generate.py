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
    def __init__(self, model=MODEL, output_dir="data"):
        self.endpoint = get_ollama_endpoint()
        self.client = ollama.Client(host=self.endpoint)
        self.model = model
        self.output_dir = output_dir
        self.dataset = []
        os.makedirs(self.output_dir, exist_ok=True)

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

    def save_data(self, filename):
        """Saves current dataset into a file."""
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, indent=4, ensure_ascii=False)

    def run(self, output_filename, samples_per_case=3, checkpoint_num=5):
        """Generator cycle."""
        current_id = 1
        path = os.path.join(self.output_dir, output_filename)

        # Trying to load from existing file
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.dataset = json.load(f)
                current_id = max((chat["id"] for chat in self.dataset)) + 1
                print(f"[*] Resuming from ID {current_id}")
            except Exception as e:
                print(f"[!] Could not read existing file: {e}")

        print(f"[*] Starting generation with model: {self.model}")

        for case_type in CASE_TYPES:
            print(f"[*] Generating '{case_type}' cases...")
            for _ in tqdm(range(samples_per_case)):
                intent = random.choice(INTENTS)
                persona = random.choice(PERSONALITIES)
                mistake = random.choice(AGENT_MISTAKES) if case_type == "agent_mistake" else "none"

                try:
                    chat_data = self.generate_single_chat(current_id, intent, case_type, persona, mistake)
                    self.dataset.append(chat_data)
                    current_id += 1
                except Exception as e:
                    print(f"[!] Error at ID {current_id}: {e}")
                    continue

                # Checkpoint
                if checkpoint_num > 0 and current_id % checkpoint_num == 0:
                    self.save_data(output_filename)

        self.save_data(output_filename)
        print(f"[+] Done! Saved {len(self.dataset)} chats to {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Customer Support Chat Dataset Generator")
    parser.add_argument("--file", type=str, default="dataset.json", help="Output file name")
    parser.add_argument("--dir", type=str, default="data", help="Output directory")
    parser.add_argument("--samples", type=int, default=3, help="Samples per case type")
    parser.add_argument("--checkpoint", type=int, default=5, help="Save every N samples (Set to 0 to disable)")
    parser.add_argument("--model", type=str, default=MODEL, help="Model to use")

    args = parser.parse_args()

    generator = ChatGenerator(model=args.model, output_dir=args.dir)
    generator.run(
        output_filename=args.file,
        samples_per_case=args.samples,
        checkpoint_num=args.checkpoint
    )
