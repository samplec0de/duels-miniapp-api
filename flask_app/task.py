from typing import List

from pymongo.database import Database


class TaskException(Exception):
    pass


class TaskNotFound(TaskException):
    pass


class Task:
    __slots__ = ('text', 'answer', 'variants', 'id', 'subject')

    def __init__(self):
        self.subject = None
        self.text = None
        self.answer = None
        self.variants = None
        self.id = None

    def from_db(self, task_id: str, subject: str, client: Database) -> None:
        collection = client[subject]
        meta = collection.find_one({'task_id': {'$eq': task_id}})
        if not meta:
            raise TaskNotFound(f"Task with id {task_id} not found.")
        self.subject = subject
        self.text = meta.get('text')
        self.answer = meta.get('answer')
        self.variants = meta.get('variants')
        self.id = task_id

    def create(self, subject: str, text: str, variants: List[str], answer: int, client: Database) -> str:
        self.subject = subject
        self.text = text
        self.answer = answer
        self.variants = variants
        collection = client[subject]
        result = collection.insert_one({'text': text, 'answer': answer, 'variants': variants})
        self.id = result.inserted_id
        return self.id

