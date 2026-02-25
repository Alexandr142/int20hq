from src.prompts import *
from src.config import *
from tqdm import tqdm
import ollama
import random
import json
import re
import os


def generate_chat(data_id, intent, case_type, personality, agent_mistake="none"):
    agent_mistake = agent_mistake if case_type == "agent_mistake" else "none"
    prompt = CHAT_GENERATION_PROMPT.format(intent=intent, case_type=case_type,
                                           personality_type=personality["type"],
                                           personality_traits=personality["traits"],
                                           mistake=agent_mistake)
    prompt += SPECIAL_REQUIREMENTS.get(case_type, "")

    response = ollama.generate(model=MODEL, prompt=prompt, format="json", options={"temperature": 0.7})
    raw_data = response["response"]

    match = re.search(r'(\{.*\}|\[.*\])', raw_data, re.DOTALL)
    clean_json = match.group(1) if match else raw_data

    json_data = {
        "id": data_id,
        "metadata":
            {
                "intent": intent,
                "case_type": case_type,
                "personality_type": personality["type"],
                "mistake": agent_mistake
            },
        "chat": json.loads(clean_json)["messages"]
    }

    return json_data


def generate_dataset(output_filename, samples_per_case=3, checkpoint_num=0):
    dataset = []
    current_id = 1

    path = "data/" + output_filename
    if os.path.exists(path):
        print("File found with similar filename. Reading and continuing from the end...")
        try:
            with open(path, 'r') as file:
                dataset = json.load(file)
            current_id = max((chat["id"] for chat in dataset)) + 1
            print("Successfully read file.")
        except:
            print("Failed to read file. After generation file will rewritten!")

    print("Starting generation...")
    for case_type in CASE_TYPES:
        print(f"Generating chats for '{case_type}' case ...")
        for _ in tqdm(range(samples_per_case)):
            intent = random.choice(INTENTS)
            personality = random.choice(PERSONALITIES)
            mistake = ""
            if case_type == "agent_mistake":
                mistake = random.choice(AGENT_MISTAKES)
            try:
                chat_data = generate_chat(current_id, intent, case_type, personality, mistake)
                dataset.append(chat_data)
            except:
                print("Failed to generate chat. Skipping.")
                continue
            if checkpoint_num != 0 and current_id % checkpoint_num == 0:
                print("Checkpoint writing. Writing to", path)
                try:
                    with open(path, 'w') as file:
                        json.dump(dataset, file, indent=4)
                    current_id += 1
                except:
                    print("Failed to write checkpoint.")
    print(f"Generated {current_id - 1}/{len(CASE_TYPES) * samples_per_case}. Writing to", path)
    with open(path, 'w') as file:
        json.dump(dataset, file, indent=4)
