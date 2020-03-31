from pathlib import Path

from flask import Flask, jsonify, request
from pymongo import MongoClient
from yaml import safe_load

app = Flask(__name__)
config = safe_load((Path(__file__).parent / "config.yml").read_text())
client = MongoClient(f"mongodb://{config['mongo']['user']}:"
                     f"{config['mongo']['password']}@{config['mongo']['host']}:"
                     f"{config['mongo']['port']}/{config['mongo']['authdb']}")
tasks_db = client['tasks']


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


if __name__ == '__main__':
    app.run()
