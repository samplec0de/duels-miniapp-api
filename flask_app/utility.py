import time
from typing import List

from pymongo import MongoClient


def unix() -> int:
    """
    This function returns current unix timestamp
    :return: int
    """
    return int(time.time())


def get_tasks(subject: str, mongo: MongoClient) -> List[str]:
    """
    Get a list of tasks by subject
    :param subject:
    :param mongo: mongo client
    :return:
    """
    collection = mongo['tasks'][subject]
    result = [str(item['_id']) for item in collection.find()]
    return result
