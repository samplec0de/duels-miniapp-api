from typing import List

from bson import ObjectId
from pymongo.database import Database


class TaskException(Exception):
    pass


class TaskNotFound(TaskException):
    pass


class EducationalTask:
    __slots__ = ('text', 'answer', 'variants', 'id', 'subject', 'weight')

    def __init__(self, task_id: str = None, subject: str = None, client: Database = None):
        self.subject = None  # предмет
        self.text = None  # текст вопроса
        self.answer = None  # индекс правильного ответа (с нуля)
        self.variants = None  # массив варивантов ответа
        self.id = None  # ObjectId в mongo
        self.weight = None  # сколько баллов будет начислено в случае верного решения
        if task_id and subject and client:
            self.from_db(task_id=task_id, subject=subject, client=client)

    def from_db(self, task_id: str, subject: str, client: Database) -> None:
        collection = client[subject]
        meta = collection.find_one({'_id': ObjectId(task_id)})
        if not meta:
            raise TaskNotFound(f"Task with id {task_id} not found.")
        self.subject = subject
        self.text = meta.get('text')
        self.answer = meta.get('answer')
        self.variants = meta.get('variants')
        self.id = meta.get('id')
        self.weight = meta.get('weight')

    def create(self, subject: str, text: str, variants: List[str], answer: int, weight: int, client: Database) -> str:
        self.subject = subject
        self.text = text
        self.answer = answer
        self.variants = variants
        self.weight = weight
        collection = client[subject]
        task_data = {
            'text': text,
            'answer': answer,
            'weight': weight,
            'variants': variants
        }
        result = collection.insert_one(task_data)
        self.id = result.inserted_id
        return self.id
