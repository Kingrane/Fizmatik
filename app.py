from mistralai import Mistral
import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User

import os

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

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            flash('Пользователь с таким email или логином уже существует')
            return redirect(url_for('signup'))
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        flash('Неверный email или пароль')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
