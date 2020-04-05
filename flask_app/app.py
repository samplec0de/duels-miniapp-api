import logging
import random
from logging.config import dictConfig
from pathlib import Path
from flask import Flask, jsonify, request
from states import TASK_PENDING
from yaml import safe_load
from flask_pymongo import PyMongo
from jsonschema import validate, ValidationError
from AppUser import AppUser
from EducationalTask import EducationalTask, TaskNotFound
from errors import UNKNOWN_SUBJECT, INVALID_USER_ID, NO_TASKS, ANSWER_REQUIRED, SUBJECT_REQUIRED, TASK_REQUIRED, \
    USER_ID_REQUIRED, SECURITY_ERROR, NO_CORRECT_ANSWER
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
app.config["MONGO_URI"] = f"mongodb://{config['mongo']['user']}:" \
                          f"{config['mongo']['password']}@{config['mongo']['host']}:" \
                          f"{config['mongo']['port']}/{config['mongo']['authdb']}"
flask_mongo = PyMongo(app)
client = flask_mongo.cx
ALLOWED_SUBJECTS = ['math', 'russian', 'informatics', 'english']


@app.route('/')
def hello_world():
    return jsonify({'version': config['core']['version']})


@app.route('/check_answer', methods=['POST'])
def check_answer():
    form_data = request.form
    if 'answer' not in form_data:
        return jsonify({"error": ANSWER_REQUIRED}), 400
    if 'subject' not in form_data:
        return jsonify({"error": SUBJECT_REQUIRED}), 400
    if 'task_id' not in form_data:
        return jsonify({"error": TASK_REQUIRED}), 400
    if 'vk_user_id' not in form_data:
        return jsonify({"error": USER_ID_REQUIRED}), 400
    answer = form_data['answer']
    subject = form_data['subject']
    task_id = form_data['task_id']
    vk_user_id = str(form_data['vk_user_id'])
    if subject not in ALLOWED_SUBJECTS:
        return jsonify({"error": UNKNOWN_SUBJECT}), 400
    if not vk_user_id.isdigit():
        return jsonify({"error": INVALID_USER_ID}), 400
    user = AppUser(vk_id=int(vk_user_id), mongo=client)
    task_state = user.task_state(task_id=task_id, subject=subject)
    if task_state != TASK_PENDING:
        return jsonify({"error": SECURITY_ERROR}), 403
    try:
        task = EducationalTask(task_id=task_id, subject=subject, mongo=client)
    except TaskNotFound as e:
        return jsonify({"error": e}), 404
    answer_correct = answer.strip() == task.answer.strip()
    if answer_correct:
        user.task_success(task_id=task_id, subject=subject)
    else:
        user.task_failed(task_id=task_id, subject=subject)
    return jsonify({"correct": answer_correct})


@app.route('/correct_answer/<subject>/<task_id>/<vk_user_id>', methods=['GET'])
def get_correct_answer(subject: str, task_id: str, vk_user_id: str):
    if subject not in ALLOWED_SUBJECTS:
        return jsonify({"error": UNKNOWN_SUBJECT}), 400
    if not vk_user_id.isdigit():
        return jsonify({"error": INVALID_USER_ID}), 400
    user = AppUser(vk_id=int(vk_user_id), mongo=client)
    task_state = user.task_state(task_id=task_id, subject=subject)
    if task_state < 0 or task_state == TASK_PENDING:
        return jsonify({"error": SECURITY_ERROR}), 403
    try:
        task = EducationalTask(task_id=task_id, subject=subject, mongo=client)
    except TaskNotFound as e:
        return jsonify({"error": e}), 404
    return jsonify({"answer": task.answer, "points": task.weight}), 200


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
    variants = task.variants
    random.shuffle(variants)
    return jsonify(
        {
            'task_id': str(task.id),
            'subject': task.subject,
            'text': task.text,
            'variants': variants
        }
    ), 200


@app.route('/tasks', methods=['POST'])
def add_task():
    json_data = request.json
    schema = {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "pattern": f"^({'|'.join(ALLOWED_SUBJECTS)})$"
            },
            "text": {"type": "string"},
            "variants": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "answer": {"type": "string"},
            "weight": {
                "type": "number",
                "minimum": 0
            }
        },
    }
    try:
        validate(instance=json_data, schema=schema)
    except ValidationError as e:
        return jsonify({"schema_error": e}), 400
    json_data['answer'] = json_data['answer'].strip()
    json_data['variants'] = [variant.strip() for variant in json_data['variants']]
    if json_data['answer'] not in json_data['variants']:
        return jsonify({"error": NO_CORRECT_ANSWER}), 400
    task = EducationalTask()
    json_data['mongo'] = client
    task.create(**json_data)
    json_data['_id'] = str(task.id)
    json_data.pop('mongo', None)
    return json_data, 201


if __name__ == '__main__':
    app.run()
