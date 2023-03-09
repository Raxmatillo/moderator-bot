import asyncio
import datetime
import logging
import re


import aiogram
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import BadRequest

from filters import IsGroup, AdminFilter
from loader import dp, bot
from aiogram.dispatcher import FSMContext



@dp.my_chat_member_handler()
async def on_chat_member_updated(
        update: types.ChatMemberUpdated,
        state: FSMContext):

    print("-"*30)
    print(update)
    print("-" * 30)

    new_chat_member = update.chat_member.new_chat_member
    chat_id = update.chat.id

    # Send a welcome message when a user joins the chat
    if new_chat_member.is_member:
        await bot.send_message(chat_id,
                               f"Welcome to the chat, {new_chat_member.first_name}!")

# @dp.register_chat_member_handler()
# async def on_chat_member_join(chat_member: types.ChatMemberUpdated):
#     print("-"*30)
#     print(chat_member)
    # chat_id = update.chat.id
    # user_id = update.new_chat_member.id
    # # Do something with the chat_id and user_id, such as send a welcome message
    # await bot.send_message(chat_id, f"Welcome, {update.new_chat_member.first_name}!")

# Register the handler



@dp.message_handler(IsGroup(), content_types=types.ContentType.ANY)
async def remove_ads_(message: types.Message):
    """
    If the message contains an entity of type 'mention', 'url', 'text_link', or 'text_mention', and the
    sender is not an admin, then delete the message and send a message saying 'Ads removed'.

    :param message: types.Message
    :type message: types.Message
    """
    chat_id = message.chat.id
    ads = ('mention', 'url', 'text_link', 'text_mention')
    entities = message.entities
    capentities = message.caption_entities
    for entity in entities:
        if entity.type in ads:
            is_admin = await AdminFilter().check(message)
            if not is_admin:
                try:
                    await message.delete()
                except Exception as e:
                    logging.error(f"{chat_id} - {e}")
                link = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>'
                text = f"<b>❗️{link} iltimos reklama tarqatmang</b>"
                message_id = (
                    await bot.send_message(message.chat.id, text)).message_id
                # await Database.add_deletemessage(chat_id=chat_id,
                #                                  message_id=message_id)

    for entity in capentities:
        if entity.type in ads:
            is_admin = await AdminFilter().check(message)
            if not is_admin:
                try:
                    await message.delete()
                except Exception as e:
                    logging.error(f"{chat_id} - {e}")
                link = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>'
                text = f"<b>❗️{link} iltimos reklama tarqatmang</b>"
                message_id = (
                    await bot.send_message(message.chat.id, text)).message_id
                # await Database.add_deletemessage(chat_id=chat_id,
                #                                  message_id=message_id)


@dp.edited_message_handler(IsGroup(), content_types=types.ContentType.ANY)
async def remove_ads_2(message: types.Message):
    chat_id = message.chat.id
    ads = ('mention', 'url', 'text_link', 'text_mention')
    entities = message.entities
    capentities = message.caption_entities
    for entity in entities:
        if entity.type in ads:
            is_admin = await AdminFilter().check(message)
            if not is_admin:
                try:
                    await message.delete()
                except Exception as e:
                    logging.error(f"{chat_id} - {e}")

                link = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>'
                text = f"<b>❗️{link} iltimos reklama tarqatmang</b>"
                message_id = (
                    await bot.send_message(message.chat.id, text)).message_id
                await Database.add_deletemessage(chat_id=chat_id,
                                                 message_id=message_id)

    for entity in capentities:
        if entity.type in ads:
            is_admin = await AdminFilter().check(message)
            if not is_admin:
                try:
                    await message.delete()
                except Exception as e:
                    logging.error(f"{chat_id} - {e}")
                link = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>'
                text = f"<b>❗️{link} iltimos reklama tarqatmang</b>"
                message_id = (
                    await bot.send_message(message.chat.id, text)).message_id
                await Database.add_deletemessage(chat_id=chat_id,
                                                 message_id=message_id)



# /ro oki !ro (read-only) komandalari uchun handler
# foydalanuvchini read-only ya'ni faqat o'qish rejimiga o'tkazib qo'yamiz.
@dp.message_handler( AdminFilter(), IsGroup(), Command("ro", prefixes="!/"))
async def read_only_mode(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id
    command_parse = re.compile(r"(!ro|/ro) ?(\d+)? ?([\w+\D]+)?")
    parsed = command_parse.match(message.text)
    time = parsed.group(2)
    comment = parsed.group(3)
    if not time:
        time = 5

    """
    !ro 
    !ro 5 
    !ro 5 test
    !ro test
    !ro test test test
    /ro 
    /ro 5 
    /ro 5 test
    /ro test
    """
    # 5-minutga izohsiz cheklash
    # !ro 5
    # command='!ro' time='5' comment=[]

    # 50 minutga izoh bilan cheklash
    # !ro 50 reklama uchun ban
    # command='!ro' time='50' comment=['reklama', 'uchun', 'ban']

    time = int(time)

    # Ban vaqtini hisoblaymiz (hozirgi vaqt + n minut)
    until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)

    try:
        await message.chat.restrict(user_id=member_id, can_send_messages=False, until_date=until_date)
        await message.reply_to_message.delete()
    except aiogram.utils.exceptions.BadRequest as err:
        await message.answer(f"Xatolik! {err.args}")
        return

    # Пишем в чат
    await message.answer(f"Foydalanuvchi {message.reply_to_message.from_user.full_name} {time} minut yozish huquqidan mahrum qilindi.\n"
                         f"Sabab: \n<b>{comment}</b>")

    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")
    # 5 sekun kutib xabarlarni o'chirib tashlaymiz
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()

# read-only holatdan qayta tiklaymiz
@dp.message_handler(IsGroup(), Command("unro", prefixes="!/"), AdminFilter())
async def undo_read_only_mode(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id

    user_allowed = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
        can_change_info=False,
        can_pin_messages=False,
    )
    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")

    await asyncio.sleep(5)
    await message.chat.restrict(user_id=member_id, permissions=user_allowed, until_date=0)
    await message.reply(f"Foydalanuvchi {member.full_name} tiklandi")

    # xabarlarni o'chiramiz
    await message.delete()
    await service_message.delete()

# Foydalanuvchini banga yuborish (guruhdan haydash)
@dp.message_handler(IsGroup(), Command("ban", prefixes="!/"), AdminFilter())
async def ban_user(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id
    await message.chat.kick(user_id=member_id)

    await message.answer(f"Foydalanuvchi {message.reply_to_message.from_user.full_name} guruhdan haydaldi")
    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")

    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()

# Foydalanuvchini bandan chiqarish, foydalanuvchini guruhga qo'sha olmaymiz (o'zi qo'shilishi mumkin)
@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"), AdminFilter())
async def unban_user(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id
    await message.chat.unban(user_id=member_id)
    await message.answer(f"Foydalanuvchi {message.reply_to_message.from_user.full_name} bandan chiqarildi")
    service_message = await message.reply("Xabar 5 sekunddan so'ng o'chib ketadi.")

    await asyncio.sleep(5)

    await message.delete()
    await service_message.delete()

