import os
import json
import random
import time
import re
from tqdm import tqdm
from google import genai
from google.genai import types

from src.prompts import CHAT_GENERATION_PROMPT
from src.config import *

# Инициализация клиента
client = genai.Client(api_key="AIzaSyAWSmy8azfYG0dzPqWqz5Z73U3fbN6asGI")


def generate_chat(data_id, intent, case_type, personality, agent_mistake="none"):
    agent_mistake = agent_mistake if case_type == "agent_mistake" else "none"
    prompt = CHAT_GENERATION_PROMPT.format(
        intent=intent,
        case_type=case_type,
        personality_type=personality["type"],
        personality_traits=personality["traits"],
        mistake=agent_mistake
    )

    config = types.GenerateContentConfig(
        temperature=0.7,
        response_mime_type="application/json",
    )

    try:
        # Используем стабильную модель 2026 года
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=config
        )

        res_json = json.loads(response.text)

        # Универсальный парсинг (если список или словарь с ключом)
        if isinstance(res_json, list):
            return res_json
        return res_json.get("messages", [])

    except Exception as e:
        error_msg = str(e)

        # Обработка лимита 429 (минутного или дневного)
        if "429" in error_msg:
            # Пытаемся найти время ожидания в тексте ошибки
            wait_match = re.search(r"retry in (\d+)", error_msg)
            wait_seconds = int(wait_match.group(1)) + 2 if wait_match else 30

            print(f"\n[!] Лимит исчерпан. Ожидание {wait_seconds}с для ID {data_id}...")
            time.sleep(wait_seconds)

            # Повторяем попытку для этого же ID
            return generate_chat(data_id, intent, case_type, personality, agent_mistake)

        print(f"\n[!] Критическая ошибка ID {data_id}: {e}")
        return None


def generate_dataset(output_filename, samples_per_case=2):
    path = "data/" + output_filename
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Загружаем существующие данные, чтобы не перезаписывать их
    dataset = []
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                dataset = json.load(file)
            print(f"Загружено {len(dataset)} существующих записей.")
        except:
            print("Файл пуст или поврежден, начинаем заново.")

    # Вычисляем актуальный ID
    current_id = max([item['id'] for item in dataset], default=0) + 1

    print(f"Запуск генерации (модель: gemini-2.5-flash)...")

    for case_type in CASE_TYPES:
        print(f"Генерация кейсов типа: {case_type}")
        for _ in tqdm(range(samples_per_case)):
            intent = random.choice(INTENTS)
            personality = random.choice(PERSONALITIES)
            mistake = random.choice(AGENT_MISTAKES) if case_type == "agent_mistake" else ""

            chat_messages = generate_chat(current_id, intent, case_type, personality, mistake)

            # Сохраняем только успешную генерацию
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

                # Сохраняем после каждого успешного чата (защита от вылета)
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(dataset, file, indent=4, ensure_ascii=False)

            # Базовая пауза для соблюдения RPM
            time.sleep(5)

    print(f"\nГотово! Всего записей в {path}: {len(dataset)}")


if __name__ == "__main__":
    # samples_per_case — сколько штук каждого типа из CASE_TYPES сделать
    generate_dataset("test_gemini_new.json", 3)