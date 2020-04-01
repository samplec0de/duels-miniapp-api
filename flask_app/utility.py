import time
from typing import List

from bson import ObjectId
from pymongo import MongoClient


def unix() -> int:
    """
    This function returns current unix timestamp
    :return: int
    """
    return int(time.time())


def get_tasks(subject: str, mongo: MongoClient) -> List[ObjectId]:
    """
    Get a list of tasks by subject
    :param subject:
    :param mongo: mongo client
    :return:
    """
    collection = mongo['tasks'][subject]
    result = [item['_id'] for item in collection.find()]
    return result


def get_user_tasks(subject: str, vk_id: int, mongo: MongoClient) -> List[ObjectId]:
    """
    Get a list of user seen tasks (solved or not)
    :param subject:
    :param vk_id:
    :param mongo: mongo client
    :return:
    """
    subj_collection = mongo['data'][f'users_{subject}']
    request = subj_collection.find_one({'vk_id': vk_id})
    if request:
        return list(request['tasks'].keys())
    else:
        return []
