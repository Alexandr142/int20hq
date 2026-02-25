import os
import json
import random
import time
import re
from tqdm import tqdm
from groq import Groq

# Импорты из твоего проекта
from src.prompts import CHAT_GENERATION_PROMPT
from src.config import *

# Инициализация клиента
# gsk_... — это ключ Groq. Убедись, что библиотека установлена: pip install groq
client = Groq(api_key="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")


def generate_chat(data_id, intent, case_type, personality, agent_mistake="none"):
    agent_mistake = agent_mistake if case_type == "agent_mistake" else "none"

    # Формируем промпт, используя данные из config.py
    prompt = CHAT_GENERATION_PROMPT.format(
        intent=intent,
        case_type=case_type,
        personality_type=personality["type"],
        personality_traits=personality["traits"],
        mistake=agent_mistake
    )

    try:
        # Запрос к Llama 3 через Groq
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system",
                 "content": "You are a professional dataset generator. Respond ONLY with JSON containing a 'messages' list."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        # Парсим JSON из ответа
        res_json = json.loads(completion.choices[0].message.content)

        if isinstance(res_json, list):
            return res_json
        return res_json.get("messages", [])

    except Exception as e:
        error_msg = str(e)
        # Если превышен лимит запросов (Rate Limit)
        if "429" in error_msg:
            print(f"\n[!] Лимит Groq. Ожидание 10с для ID {data_id}...")
            time.sleep(10)
            return generate_chat(data_id, intent, case_type, personality, agent_mistake)

        print(f"\n[!] Ошибка Groq ID {data_id}: {e}")
        return None


def generate_dataset(output_filename, samples_per_case=2):
    path = "data/" + output_filename
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Загружаем старые данные, чтобы продолжить, а не перезаписывать
    dataset = []
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                dataset = json.load(file)
            print(f"Загружено {len(dataset)} существующих записей.")
        except:
            print("Начинаем новый файл.")

    # Считаем ID
    current_id = max([item['id'] for item in dataset], default=0) + 1
    print(f"Запуск генерации через Groq (модель llama3-8b-8192)...")

    for case_type in CASE_TYPES:
        print(f"Генерация кейсов типа: {case_type}")
        for _ in tqdm(range(samples_per_case)):
            intent = random.choice(INTENTS)
            personality = random.choice(PERSONALITIES)
            mistake = random.choice(AGENT_MISTAKES) if case_type == "agent_mistake" else ""

            chat_messages = generate_chat(current_id, intent, case_type, personality, mistake)

            if chat_messages:
                dataset.append({
                    "id": current_id,
                    "metadata": {
                        "intent": intent,
                        "case_type": case_type,
                        "personality_type": personality["type"],
                        "mistake": mistake
                    },
                    "chat": chat_messages
                })
                current_id += 1

                # Сохраняем после каждого шага
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(dataset, file, indent=4, ensure_ascii=False)

            # У Groq лимиты выше, пауза может быть минимальной
            time.sleep(1)

    print(f"\nГотово! Файл сохранен: {path}")


if __name__ == "__main__":
    # 5 — это сколько чатов сделать для каждого типа из CASE_TYPES
    generate_dataset("test_groq_data.json", 5)