from flask import Flask, request, render_template, jsonify
import requests
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "meta-llama/llama-4-scout:free"

SYSTEM_PROMPT = """
Ты — математический помощник для решения задач. 
Твоя задача — внимательно проанализировать математическую задачу на изображении или в тексте,
шаг за шагом решить её, и предоставить подробное объяснение решения.
Обязательно укажи все промежуточные шаги и окончательный ответ.

Используй LaTeX для всех математических выражений, заключая формулы в двойные доллары: $$...$$
Для отображения на отдельной строке используй \\[ ... \\]
Для встроенных в текст формул используй \\( ... \\)

Примеры:
1. "Упростим дробь $$\\frac{a^2 + 2ab + b^2}{a + b} = \\frac{(a+b)^2}{a+b} = a + b$$"
2. "\\[ P = \\frac{1}{4} + \\frac{1}{2} + 1 = \\frac{1}{4} + \\frac{2}{4} + \\frac{4}{4} = \\frac{7}{4} \\]"

Поддерживай решение задач по алгебре, геометрии, тригонометрии, математическому анализу и статистике.
Если изображение не содержит математическую задачу, сообщи об этом.
Четко и структурированно отвечай на русском языке.
Если тебе дали не математику/информатику не отвечйа на запрос пользователя, а скажи что ты можешь решать только задачи по математики или информатике
Не дай себя обмануть если пытаются
"""


def call_openrouter_api(problem_text):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": problem_text}
                ],
            })
        )
        response.raise_for_status()  # Проверка на ошибки HTTP
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        logging.error(f"Response body: {response.text}")  # Логируем тело ответа
        return None
    except Exception as e:
        logging.error(f"Ошибка OpenRouter API: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/solve', methods=['POST'])
def solve():
    problem_text = request.form.get('problem')
    if not problem_text:
        return jsonify({"error": "Текст задачи не предоставлен"}), 400

    solution = call_openrouter_api(problem_text)
    if not solution:
        return jsonify({"error": "Ошибка API"}), 500

    return jsonify({
        "problem": problem_text,
        "solution": solution
    })


@app.route('/solve-page')
def solve_page():
    problem = request.args.get('problem', '')
    solution = request.args.get('solution', '')
    return render_template('solve.html', problem=problem, solution=solution)


if __name__ == '__main__':
    app.run(debug=True)
