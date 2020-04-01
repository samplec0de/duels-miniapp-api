from pymongo import MongoClient

from flask_app.EducationalTask import EducationalTask
from flask_app.states import TASK_SUCCESS, TASK_FAILED, TASK_PENDING
from flask_app.utility import unix


class AppUser:
    __slots__ = ('id', 'vk_id', 'rating', 'mongo')

    def __init__(self, vk_id: int, mongo: MongoClient):
        self.id = None  # ObjectId из mongo
        self.vk_id = vk_id  # user_id из vk api
        self.rating = None  # рейтинг игрока
        self.mongo = mongo
        data = self._find()
        if data:
            self.id = data.get('_id')
            self.vk_id = data.get('vk_id')
            self.rating = data.get('rating')
        else:
            user = {'vk_id': self.vk_id, 'rating': 0}
            self.id = self.mongo['data']['users'].insert_one(user).inserted_id

    def _find(self) -> dict:
        return self.mongo['data']['users'].find_one({'vk_id': self.vk_id})

    def give_task(self, task_id: str, subject: str) -> None:
        """
        Set pending state for task (like "give" task to user)
        :param task_id:
        :param subject:
        :return:
        """
        # tasks - словарь. ключ: task_id, значение: (статус, unix time stamp) (task_id: статус)
        subj_collection = self.mongo['data'][f'users_{subject}']
        result = subj_collection.find_one({'_id': self.id})
        if result:
            tasks = result['tasks']
            tasks[task_id] = (TASK_PENDING, unix())
            subj_collection.find_one_and_update({'vk_id': self.vk_id}, {'$set': {'tasks': tasks}})
        else:
            tasks = {task_id: (TASK_PENDING, unix())}
            subj_collection.insert_one({'vk_id': self.vk_id, 'tasks': tasks})

    def task_success(self, task_id: str, subject: str) -> None:
        """
        Set success state for task (user successfully solved task)
        :param task_id:
        :param subject:
        :return:
        """
        task = EducationalTask(task_id=task_id, subject=subject, mongo=self.mongo)
        self.rating += task.weight
        subj_collection = self.mongo['data'][f'users_{subject}']
        result = subj_collection.find_one({'vk_id': self.vk_id})
        tasks = result['tasks']
        tasks[task_id] = (TASK_SUCCESS, unix())
        subj_collection.find_one_and_update({'vk_id': self.vk_id}, {'$set': {'tasks': tasks}})
        self.mongo['data']['users'].find_one_and_update({'_id': self.id}, {'$set': {'rating': self.rating}})

    def task_failed(self, task_id: str, subject: str) -> None:
        """
        Set failed state for task (user failed task)
        :param task_id:
        :param subject:
        :return:
        """
        subj_collection = self.mongo['data'][f'users_{subject}']
        result = subj_collection.find_one({'_id': self.id})
        tasks = result['tasks']
        tasks[task_id] = (TASK_FAILED, unix())
        subj_collection.find_one_and_update({'vk_id': self.vk_id}, {'$set': {'tasks': tasks}})
