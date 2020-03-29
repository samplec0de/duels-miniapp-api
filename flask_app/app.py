from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/tasks/<subject>/<difficulty>/<task_id>', methods=['GET'])
def get_subject(subject, difficulty, task_id):
    if subject not in ["math", "informatics", "russian"]:
        return jsonify({"error": "unknown subject"}), 400
    if not difficulty.isdigit() or int(difficulty) < 1 or int(difficulty) > 3:
        return jsonify({"error": "incorrect difficulty"}), 400
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
    return jsonify({"subject": subject, "id": task_id, "difficulty": difficulty, "task": tasks[subject][int(task_id)]}), 200


@app.route('/check_answer', methods=['POST'])
def check_answer():
    form_data = request.form
    if 'answer' not in form_data:
        return jsonify({"error": "answer is required form-data key"}), 400
    if 'subject' not in form_data:
        return jsonify({"error": "subject is required form-data key"}), 400
    if 'task_id' not in form_data:
        return jsonify({"error": "task_id is required form-data key"}), 400
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
