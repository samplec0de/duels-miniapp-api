from bson import ObjectId
from pymongo.database import Database

from flask_app.states import TASK_SUCCESS, TASK_FAILED, TASK_PENDING
from flask_app.utility import unix


class User:
    __slots__ = ('id', 'vk_id', 'tasks', 'client', 'collection')

    def __init__(self, vk_id: int, client: Database):
        self.id = None  # ObjectId из mongo
        self.vk_id = vk_id  # user_id из vk api
        self.tasks = None  # словарь task_id, которые были ПОКАЗАНЫ пользователю (task_id: статус)
        self.collection = client['data']['users']
        data = self._find()
        if data:
            self.id = data.get('_id')
            self.vk_id = data.get('vk_id')
            self.tasks = data.get('tasks')
        else:
            user = {'vk_id': self.vk_id, 'tasks': dict()}
            self.id = self.collection.insert_one(user).inserted_id

    def _find(self) -> dict:
        return self.collection.find_one({'vk_id': {'$eq': self.vk_id}})

    def add_task(self, task_id: str) -> None:
        self.tasks[ObjectId(task_id)] = (TASK_PENDING, unix())
        self.collection.find_one_and_update({'_id': self.id}, {'tasks': self.tasks})

    def task_success(self, task_id: str) -> None:
        self.tasks[ObjectId(task_id)] = (TASK_SUCCESS, unix())
        self.collection.find_one_and_update({'_id': self.id}, {'tasks': self.tasks})

    def task_failed(self, task_id: str) -> None:
        self.tasks[ObjectId(task_id)] = (TASK_FAILED, unix())
        self.collection.find_one_and_update({'_id': self.id}, {'tasks': self.tasks})
