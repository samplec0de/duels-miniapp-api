from pymongo.database import Database


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
