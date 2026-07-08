import asyncio
import logging

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
                InlineKeyboardButton(text="Да", callback_data=f"{prefix}:yes"),
                InlineKeyboardButton(text="Нет", callback_data=f"{prefix}:no"),
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
    await message.answer("ты пьёшь алкоголь?🤔🤔🥂🍷🍾", reply_markup=yes_no_kb("drink"))
    await state.set_state(Form.drink)


@router.callback_query(Form.drink, F.data.startswith("drink:"))
async def process_drink(callback: CallbackQuery, state: FSMContext):
    answer = callback.data.split(":")[1]
    await state.update_data(drink=answer)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "а останешься на ночь?🥺🥺🥺😴😴 (кол-во мест ограничено, возможно придётся ютиться!!)", reply_markup=yes_no_kb("stay")
    )
    await state.set_state(Form.stay)
    await callback.answer()


@router.callback_query(Form.stay, F.data.startswith("stay:"))
async def process_stay(callback: CallbackQuery, state: FSMContext):
    answer = callback.data.split(":")[1]
    await state.update_data(stay=answer)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "ээээ, пожелания по еде будут какиенить? шашлык 100% будэ, салатики бурмалдатики мб, пиццо + алисо сосисо в тесте"
    )
    await state.set_state(Form.food_wishes)
    await callback.answer()


@router.message(Form.food_wishes)
async def process_food_wishes(message: Message, state: FSMContext):
    await state.update_data(food_wishes=message.text)
    data = await state.get_data()

    if data.get("drink") == "yes":
        await message.answer(
            "УРААААААААААА!!!!🎉🎉 а что именно хош выпить? любые пожелания (+ будет велком дринк, его обязательно надо будэ выпить!"
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
        f"если ничего не приглянулось, то дари как знаешь, мне в любом случае приятно будет!"
        f"{RULES_TEXT}\n\n"
        "другую нужную инфу буду писать уже в беседе, а так буду ждать на тусе <3"
    )
    await message.answer(final_text, disable_web_page_preview=True)

    await notify_admin(message.from_user, data)
    await state.clear()


async def notify_admin(user, data: dict):
    username = f"@{user.username}" if user.username else "(без username)"
    full_name = user.full_name

    drink_text = "Пьёт 🍷" if data.get("drink") == "yes" else "Не пьёт 🚫"
    stay_text = "Остаётся на ночь 🌙" if data.get("stay") == "yes" else "Не остаётся"
    food_wishes = data.get("food_wishes") or "-"
    alcohol_wishes = data.get("alcohol_wishes")

    text = (
        "📩 <b>Новый ответ гостя</b>\n\n"
        f"Имя: {full_name}\n"
        f"Username: {username}\n"
        f"ID: {user.id}\n\n"
        f"{drink_text}\n"
        f"{stay_text}\n"
        f"Пожелания по еде: {food_wishes}\n"
    )
    if alcohol_wishes is not None:
        text += f"Пожелания по алкоголю: {alcohol_wishes}\n"

    await bot.send_message(ADMIN_ID, text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())