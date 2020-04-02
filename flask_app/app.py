import logging
import random
from logging.config import dictConfig
from pathlib import Path

from flask import Flask, jsonify, request
from pymongo import MongoClient
from yaml import safe_load

from AppUser import AppUser
from EducationalTask import EducationalTask
from errors import UNKNOWN_SUBJECT, INVALID_USER_ID, NO_TASKS
from utility import get_tasks

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
app = Flask(__name__)
config = safe_load((Path(__file__).parent / "config.yml").read_text())
client = MongoClient(f"mongodb://{config['mongo']['user']}:{config['mongo']['password']}@{config['mongo']['host']}:"
                     f"{config['mongo']['port']}/{config['mongo']['authdb']}")
ALLOWED_SUBJECTS = ['math', 'russian', 'informatics', 'english']


@app.route('/')
def hello_world():
    return jsonify({'version': config['core']['version']})


@app.route('/tasks/<subject>/<task_id>', methods=['GET'])
def get_subject(subject, task_id):
    if subject not in ["math", "informatics", "russian"]:
        return jsonify({"error": "unknown subject"}), 400
    if not task_id.isdigit() or int(task_id) not in [0, 1, 2]:
        return jsonify({"error": "task id not found"}), 404
    tasks = {
        "math": {
            0: "Сколько будет 1 + 2?",
            1: "Сколько ног у двух людей?",
            2: "Вычислите: 2 + 2 * 2"
        },
        "informatics": {
            0: "Сколько бит в одном байте?",
            1: "Занимался ли информатикой Алан Тьюринг?",
            2: "Существует ли в c++ библиотека iostream?"
        },
        "russian": {
            0: "В каком слове не правильно выделена буква ударения: мАма, сИроты, питОн",
            1: "А тут мне просто лень думать и верный ответ: 48",
            2: "Снова лень думать, ответ: 2",
        }
    }
    return jsonify({"subject": subject, "id": task_id, "task": tasks[subject][int(task_id)]}), 200


@app.route('/check_answer', methods=['POST'])
def check_answer():
    form_data = request.form
    if 'answer' not in form_data:
        return jsonify({"error": "answer is required form-data key"}), 401
    if 'subject' not in form_data:
        return jsonify({"error": "subject is required form-data key"}), 402
    if 'task_id' not in form_data:
        return jsonify({"error": "task_id is required form-data key"}), 403
    answer = form_data['answer']
    subject = form_data['subject']
    task_id = form_data['task_id']
    if subject not in ["math", "informatics", "russian"]:
        return jsonify({"error": "unknown subject"}), 400
    if not task_id.isdigit() or int(task_id) not in [0, 1, 2]:
        return jsonify({"error": "task id not found"}), 404
    answers = {
        "math": {
            0: "3",
            1: "4",
            2: "6"
        },
        "informatics": {
            0: "8",
            1: "да",
            2: "да"
        },
        "russian": {
            0: "сироты",
            1: "48",
            2: "2",
        }
    }
    correct = answers[subject][int(task_id)]
    if correct == answer:
        return jsonify({"correct": True, "correct_answer": correct}), 200
    else:
        return jsonify({"correct": False, "correct_answer": correct}), 200


@app.route('/tasks/random/<subject>/<vk_user_id>', methods=['GET'])
def random_task(subject: str, vk_user_id: str):
    if subject not in ALLOWED_SUBJECTS:
        return jsonify({'error': UNKNOWN_SUBJECT}), 400
    if not vk_user_id.isdigit():
        return jsonify({'error': INVALID_USER_ID}), 400
    user = AppUser(vk_id=int(vk_user_id), mongo=client)
    tasks = set(get_tasks(subject=subject, mongo=client))
    user_tasks = set(user.get_tasks(subject=subject))
    available_tasks = tasks.difference(user_tasks)
    if not available_tasks:
        return jsonify({'error': NO_TASKS}), 200
    task_id = str(random.choice(list(available_tasks)))
    user.give_task(task_id=task_id, subject=subject)
    task = EducationalTask(task_id=task_id, subject=subject, mongo=client)
    return jsonify(
        {
            'task_id': str(task.id),
            'subject': task.subject,
            'text': task.text,
            'variants': task.variants
        }
    ), 200


if __name__ == '__main__':
    app.run()
