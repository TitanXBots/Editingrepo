database.py
# TitanXBots MongoDB management

import pymongo
from config import DB_URI, DB_NAME, OWNER_ID

# -------------------------------
# Database connection
# -------------------------------
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

# Collections
user_data = database['users']
banned_users = database['banned_users']


# -------------------------------
# Seishiro Database Manager
# -------------------------------
class SeishiroDB:

    # -------------------------------
    # USER MANAGEMENT
    # -------------------------------
    async def present_user(self, user_id: int) -> bool:
        return user_data.find_one({'_id': user_id}) is not None

    async def add_user(self, user_id: int):
        user_data.update_one(
            {'_id': user_id},
            {'$set': {'_id': user_id}},
            upsert=True
        )

    async def full_userbase(self) -> list:
        return [doc['_id'] for doc in user_data.find()]

    async def total_users(self) -> int:
        return user_data.count_documents({})

    async def del_user(self, user_id: int):
        user_data.delete_one({'_id': user_id})





    # -------------------------------
    # BAN MANAGEMENT
    # -------------------------------
    async def is_user_banned(self, user_id: int) -> bool:
        return banned_users.find_one({'_id': user_id}) is not None

    async def get_ban_reason(self, user_id: int):
        data = banned_users.find_one({'_id': user_id})
        return data.get('reason', 'No reason provided') if data else None

    async def ban_user(self, user_id: int, reason: str):
        banned_users.update_one(
            {'_id': user_id},
            {'$set': {'reason': reason}},
            upsert=True
        )

    async def unban_user(self, user_id: int):
        banned_users.delete_one({'_id': user_id})

    async def banned_users_list(self):
        return list(banned_users.find())


    # -------------------------------
    # ADMIN CHECK (OWNER ONLY)
    # -------------------------------
    async def is_admin(self, user_id: int) -> bool:
        return user_id == OWNER_ID
