from pymongo.database import Database


class User:
    __slots__ = ('id', 'vk_id', 'solved_tasks', 'client', 'collection')

    def __init__(self, vk_id: int, client: Database):
        self.id = None
        self.vk_id = vk_id
        self.solved_tasks = None
        self.client = client
        self.collection = self.client['users']['vk_users']
        data = self._find()
        if data:
            self.id = data['_id']
            self.vk_id = data['vk_id']
            self.solved_tasks = data['solved_tasks']
        else:
            user = {'vk_id': self.vk_id, 'solved_tasks': []}
            self.id = self.collection.insert_one(user).inserted_id

    def _find(self) -> Document:
        return self.collection.find_one({'vk_id': {'$eq': self.vk_id}})
