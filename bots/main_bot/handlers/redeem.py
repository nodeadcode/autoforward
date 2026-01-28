from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import AsyncSessionLocal
from database.crud import redeem_code, create_redeem_code
from bots.main_bot.keyboards.inline import back_home_kb
from config.settings import OWNER_ID
import uuid

router = Router()

class RedeemStates(StatesGroup):
    waiting_for_code = State()

@router.callback_query(F.data == "redeem")
async def cb_redeem(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎁 **Redeem Code**\n\n"
        "Please enter your redemption code below:",
        reply_markup=back_home_kb()
    )
    await state.set_state(RedeemStates.waiting_for_code)

@router.message(RedeemStates.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    user_id = message.from_user.id
    
    async with AsyncSessionLocal() as db:
        success = await redeem_code(db, user_id, code)
    
    if success:
        await message.answer(
            "🎉 **Success!**\n\n"
            "Your plan has been extended.",
            reply_markup=back_home_kb()
        )
    else:
        await message.answer(
            "❌ **Invalid or Used Code**\n\nPlease try again or contact support.",
            reply_markup=back_home_kb()
        )
    await state.clear()

# Owner Command: /gencode <days>
@router.message(Command("gencode"))
async def cmd_gencode(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /gencode <days>")
        return
    
    try:
        days = int(args[1])
        code = f"SPINIFY-{str(uuid.uuid4())[:8].upper()}"
        
        async with AsyncSessionLocal() as db:
            await create_redeem_code(db, code, days)
        
        await message.answer(f"✅ Code Generated:\n\n`{code}`\n\nDuration: {days} days")
    except ValueError:
        await message.answer("Invalid number of days.")
