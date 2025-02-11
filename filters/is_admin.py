from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import ADMINS

class AdminFilter(BoundFilter):
    async def check(self, message: types.Message):
        print("is_admin:", str(message.from_user.id) in str(ADMINS))
        return str(message.from_user.id) in str(ADMINS)