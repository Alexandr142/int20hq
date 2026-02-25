from src.prompts import CHAT_GENERATION_PROMPT
from src.config import *
from tqdm import tqdm
import ollama
import random
import json


def generate_chat(data_id, intent, case_type, personality, agent_mistake="none"):
    agent_mistake = agent_mistake if case_type == "agent_mistake" else "none"
    prompt = CHAT_GENERATION_PROMPT.format(intent=intent, case_type=case_type,
                                           personality_type=personality["type"],
                                           personality_traits=personality["traits"],
                                           mistake=agent_mistake)
    response = ollama.generate(
        model=MODEL,
        prompt=prompt,
        format="json",
        options={"temperature": 0.7}
    )

    json_data = {
        "id": data_id,
        "metadata":
        {
            "intent": intent,
            "case_type": case_type,
            "personality_type": personality["type"],
            "mistake": agent_mistake
        },
        "chat": json.loads(response["response"])["messages"]
    }

    return json_data


def generate_dataset(output_filename, samples_per_case=3):
    dataset = []
    current_id = 1
    print("Starting generation...")
    for case_type in CASE_TYPES:
        print("Generating chats for", case_type, "...")
        for i in tqdm(range(samples_per_case)):
            intent = random.choice(INTENTS)
            personality = random.choice(PERSONALITIES)
            mistake = ""
            if case_type == "agent_mistake":
                mistake = random.choice(AGENT_MISTAKES)
            chat_data = generate_chat(current_id, intent, case_type, personality, mistake)
            dataset.append(chat_data)
            current_id += 1
    path = "data/" + output_filename
    print("Generation successful. Writing to", path)
    with open(path, 'w') as file:
        json.dump(dataset, file, indent=4)


if __name__ == "__main__":
    generate_dataset("test.json", 5)

