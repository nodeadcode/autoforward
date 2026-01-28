from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bots.login_bot.handlers.start import LoginStates

router = Router()

@router.message(LoginStates.waiting_for_api_id)
async def process_api_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ API ID must be a number using digits. Please try again:")
        return
    
    await state.update_data(api_id=int(message.text))
    await message.answer("✅ API ID saved.\n\n👇 Now send your **API Hash**:")
    await state.set_state(LoginStates.waiting_for_api_hash)

@router.message(LoginStates.waiting_for_api_hash)
async def process_api_hash(message: types.Message, state: FSMContext):
    if len(message.text) < 10:
        await message.answer("❌ Invalid API Hash. It looks too short. Please try again:")
        return

    await state.update_data(api_hash=message.text)
    await message.answer("✅ API credentials saved.\n\n👇 Now send your **Phone Number** (with country code, e.g., +1234567890):")
    await state.set_state(LoginStates.waiting_for_phone)
