from pymongo.database import Database


class User:
    __slots__ = ('user_id')

    def __init__(self, user_id: int):
        self.user_id = user_id

    def find(self, client: Database) -> bool:
        collection = client['users']['vk_users']
        return collection.find_one({'vk_id': {'$eq': self.user_id}})