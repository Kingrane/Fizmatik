from flask import Flask, request, render_template, jsonify
from mistralai import Mistral
import os
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "wR1Cp3zVnrh13YXW2z2USxNQsqhNuOPZ")
MODEL = "pixtral-12b-2409"

# Оригинальный системный промпт без изменений
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


def get_mistral_client():
    try:
        return Mistral(api_key=MISTRAL_API_KEY)
    except Exception as e:
        logging.error(f"Ошибка Mistral: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/solve', methods=['POST'])
def solve():
    problem_text = request.form.get('problem')
    if not problem_text:
        return jsonify({"error": "Текст задачи не предоставлен"}), 400

    client = get_mistral_client()
    if not client:
        return jsonify({"error": "Ошибка API"}), 500

    try:
        response = client.chat.complete(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": problem_text}
            ]
        )
        return jsonify({
            "problem": problem_text,
            "solution": response.choices[0].message.content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/solve-page')
def solve_page():
    # Новая функция для отображения страницы с решением
    problem = request.args.get('problem', '')
    solution = request.args.get('solution', '')
    return render_template('solve.html', problem=problem, solution=solution)


if __name__ == '__main__':
    app.run(debug=True)
