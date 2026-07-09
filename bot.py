import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "бурмалда")

GROUP_LINK = os.getenv("GROUP_LINK", "бурмалда")

WISHLIST_LINK = os.getenv("WISHLIST_LINK", "бурмалда")

ADMIN_ID = int(os.getenv("ADMIN_ID", "бурмалда"))

RULES_TEXT = (
    "**правила нах:<**\n"
    "1. блевать запрещено!! ⛔️ \n"
    "2. драться тоже запрещено \n"
    "3. ломать чето тоже пожалуйста не надо \n"
    "4. с собой обязательно хорошее настроение!!!!!😍😍😍😍 \n"
    "5. ээээ\n"
    "6. чёто еще\n"
    "7. итд"
)

MESSAGE_DELAY = 1.5

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


class Form(StatesGroup):
    drink = State()
    stay = State()
    food_wishes = State()
    alcohol_wishes = State()


def yes_no_kb(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ДА!!1!", callback_data=f"{prefix}:yes"),
                InlineKeyboardButton(text="нет....", callback_data=f"{prefix}:no"),
            ]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"привет, {message.from_user.first_name}!!!\n"
        "я оч рада, что ты будешь на моем дэрэ :)\n"
        "ответь, пожалуйста, на пару вопросов, чтобы я подготовила всё как надо"
    )
    await asyncio.sleep(MESSAGE_DELAY)
    await message.answer("ты пьёшь алкоголь?🤔🤔🥂🍷🍾", reply_markup=yes_no_kb("drink"))
    await state.set_state(Form.drink)


@router.callback_query(Form.drink, F.data.startswith("drink:"))
async def process_drink(callback: CallbackQuery, state: FSMContext):
    answer = callback.data.split(":")[1]
    await state.update_data(drink=answer)

    await callback.message.delete()
    await asyncio.sleep(MESSAGE_DELAY)
    await callback.message.answer(
        "а останешься на ночь?🥺🥺🥺😴😴 (кол-во мест ограничено, возможно придётся ютиться!!)",
        reply_markup=yes_no_kb("stay"),
    )
    await state.set_state(Form.stay)
    await callback.answer()


@router.callback_query(Form.stay, F.data.startswith("stay:"))
async def process_stay(callback: CallbackQuery, state: FSMContext):
    answer = callback.data.split(":")[1]
    await state.update_data(stay=answer)

    await callback.message.delete()
    await asyncio.sleep(MESSAGE_DELAY)
    await callback.message.answer(
        "ээээ, пожелания по еде будут какиенить? шашлык 100% будэ, "
        "салатики бурмалдатики мб, пиццо + алисо сосисо в тесте"
    )
    await state.set_state(Form.food_wishes)
    await callback.answer()


@router.message(Form.food_wishes)
async def process_food_wishes(message: Message, state: FSMContext):
    await state.update_data(food_wishes=message.text)
    data = await state.get_data()

    if data.get("drink") == "yes":
        await asyncio.sleep(MESSAGE_DELAY)
        await message.answer(
            "УРААААААААААА!!!!🎉🎉 а что именно хош выпить? любые пожелания "
            "(+ будет велком дринк, его обязательно надо будэ выпить! "
            "(или отправь «-», если пожеланий нет или придёшь сос воим)"
        )
        await state.set_state(Form.alcohol_wishes)
    else:
        await finish_form(message, state)


@router.message(Form.alcohol_wishes)
async def process_alcohol_wishes(message: Message, state: FSMContext):
    await state.update_data(alcohol_wishes=message.text)
    await finish_form(message, state)


async def finish_form(message: Message, state: FSMContext):
    data = await state.get_data()

    final_text = (
        "спс большое за ответы!! вся нужная инфа будет снизу:\n\n"
        f"беседа: {GROUP_LINK}\n\n"
        f"мой вишлист: {WISHLIST_LINK}\n"
        f"(пс: большая просьба зарегаться там и забронировать подарок :)\n"
        f"если ничего не приглянулось, то дари как знаешь, мне в любом случае приятно будет!\n\n"
        f"{RULES_TEXT}\n\n"
        "другую нужную инфу буду писать уже в беседе, а так буду ждать на тусе <3"
    )
    await asyncio.sleep(MESSAGE_DELAY)
    await message.answer(final_text, disable_web_page_preview=True)

    await notify_admin(message.from_user, data)
    await state.clear()


async def notify_admin(user, data: dict):
    username = f"@{user.username}" if user.username else "(без username)"
    full_name = user.full_name

    drink_text = "пьёт" if data.get("drink") == "yes" else "не пьет"
    stay_text = "остается на ночь" if data.get("stay") == "yes" else "не остается"
    food_wishes = data.get("food_wishes") or "-"
    alcohol_wishes = data.get("alcohol_wishes")

    text = (
        "новый ответ гостя:\n\n"
        f"имя: {full_name}\n"
        f"юзер: {username}\n"
        f"айди: {user.id}\n\n"
        f"{drink_text}\n"
        f"{stay_text}\n"
        f"пожелания по еде: {food_wishes}\n"
    )
    if alcohol_wishes is not None:
        text += f"пожелания по алко: {alcohol_wishes}\n"

    await bot.send_message(ADMIN_ID, text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
