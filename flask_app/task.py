from pymongo.database import Database

ALLOWED_SUBJECTS = ['math', 'russian', 'informatics', 'english']


class TaskException(Exception):
    pass


class TaskSubjectIncorrect(TaskException):
    pass


class TaskIdTypeNotInt(TaskException):
    pass


class SubjectTypeNotStr(TaskException):
    pass


class TaskNotFound(TaskException):
    pass


class Task:
    __slots__ = ('text', 'answer', 'variants')

    def __init__(self):
        self.text = None
        self.answer = None
        self.variants = None

    def from_db(self, task_id: int, subject: str, client: Database):
        if subject not in ALLOWED_SUBJECTS:
            raise TaskSubjectIncorrect(f"Subject {subject} is not allowed")
        if type(task_id) != int:
            raise TaskIdTypeNotInt(f"Task id type {type(task_id)} is not allowed.")
        if type(subject) != str:
            raise SubjectTypeNotStr(f"Subject type {type(task_id)} is not allowed.")
        collection = client[subject]
        meta = collection.find_one({'task_id': {'$in': task_id}})
        if not meta:
            raise TaskNotFound(f"Task with id {task_id} not found.")
        self.text = meta.get('text')
        self.answer = meta.get('answer')
        self.variants = meta.get('variants')
