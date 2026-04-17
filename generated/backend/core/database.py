from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "forgeapi")


@lru_cache(maxsize=1)
def get_client():
    return MongoClient(MONGODB_URL)


def get_database():
    return get_client()[DATABASE_NAME]


def get_collection(name: str):
    return get_database()[name]


def ping_database():
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False
