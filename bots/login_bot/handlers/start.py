from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class LoginStates(StatesGroup):
    waiting_for_api_id = State()
    waiting_for_api_hash = State()
    waiting_for_phone = State()
    waiting_for_otp = State()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❉ **LOGIN ASSISTANT** ❉\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Connect your account safely and securely.\n"
        "◈ Get keys at: `my.telegram.org`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⊹ Please send your **API ID** to begin:"
    )
    await state.set_state(LoginStates.waiting_for_api_id)
