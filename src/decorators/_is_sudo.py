from functools import wraps

from src.database import db
from src.utils import extract_data


def is_sudo(callback):

    @wraps(callback)
    async def wrapper(update, context):
        user = extract_data(update)[1]
        if await db.is_sudo(user.id):
            return await callback(update, context)

    return wrapper
