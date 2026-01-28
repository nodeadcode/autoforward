from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from bots.login_bot.handlers.start import LoginStates

router = Router()

@router.message(LoginStates.waiting_for_api_id)
async def process_api_id(message: types.Message, state: FSMContext):
    api_id = message.text.strip()
    if not api_id.isdigit():
        await message.answer("◊ **ERROR**: API ID must be numeric.\n⊹ Please try again:")
        return
    
    await state.update_data(api_id=int(api_id))
    await message.answer("◈ **API ID SAVED**\n━━━━━━━━━━━━━━━━━━━━\n⊹ Now send your **API HASH**:")
    await state.set_state(LoginStates.waiting_for_api_hash)

@router.message(LoginStates.waiting_for_api_hash)
async def process_api_hash(message: types.Message, state: FSMContext):
    api_hash = message.text.strip()
    if len(api_hash) < 10:
        await message.answer("◊ **ERROR**: API HASH seems too short.\n⊹ Please try again:")
        return

    await state.update_data(api_hash=api_hash)
    await message.answer("◈ **API HASH SAVED**\n━━━━━━━━━━━━━━━━━━━━\n⊹ Send your **PHONE NUMBER** (with +country code):")
    await state.set_state(LoginStates.waiting_for_phone)
