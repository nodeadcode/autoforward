from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import AsyncSessionLocal
from database.crud import get_user_settings
from database.models import Settings
from bots.main_bot.keyboards.inline import settings_kb, back_home_kb
from config.settings import MIN_MESSAGE_INTERVAL_MINUTES

router = Router()

class SettingsStates(StatesGroup):
    waiting_for_interval = State()

@router.callback_query(F.data == "settings")
async def cb_settings(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    async with AsyncSessionLocal() as db:
        settings = await get_user_settings(db, user_id)
        if not settings:
            # Should have been created on start, but safety first
            from database.crud import get_or_create_user
            await get_or_create_user(db, user_id)
            settings = await get_user_settings(db, user_id)

        await callback.message.edit_text(
            "❉ **SYSTEM SETTINGS** ❉\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"◈ **Interval**: `{settings.interval_minutes}` minutes\n"
            f"◈ **Night Mode**: {'◈ ON' if settings.night_mode_enabled else '◊ OFF'}\n"
            f"◈ **Scheduler**: {'◈ RUNNING' if settings.active else '◊ PAUSED'}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⊹ Configure your automation behavior below:",
            reply_markup=settings_kb(settings.night_mode_enabled, settings.active)
        )

@router.callback_query(F.data == "toggle_night")
async def cb_toggle_night(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with AsyncSessionLocal() as db:
        settings = await get_user_settings(db, user_id)
        settings.night_mode_enabled = not settings.night_mode_enabled
        await db.commit()
        # Refresh UI
        await cb_settings(callback)

@router.callback_query(F.data == "toggle_active")
async def cb_toggle_active(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with AsyncSessionLocal() as db:
        from database.crud import is_plan_active
        if not await is_plan_active(db, user_id):
            await callback.answer("❌ Your plan has expired. Please redeem a code to continue.", show_alert=True)
            return

        from database.models import Session
        from sqlalchemy.future import select
        res = await db.execute(select(Session).where(Session.user_id == user_id))
        session = res.scalar_one_or_none()

        settings = await get_user_settings(db, user_id)
        
        if not settings.active: # Trying to turn it ON
            if not (session and session.is_active):
                await callback.answer("❌ Cannot start scheduler without a connected account!", show_alert=True)
                return
        
        settings.active = not settings.active
        await db.commit()
        await cb_settings(callback)

@router.callback_query(F.data == "set_interval")
async def cb_set_interval(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        f"⏱ **Set Interval**\n\n"
        f"Please enter the time interval in minutes.\n"
        f"Minimum allowed: {MIN_MESSAGE_INTERVAL_MINUTES} minutes.",
        reply_markup=back_home_kb()
    )
    await state.set_state(SettingsStates.waiting_for_interval)

@router.message(SettingsStates.waiting_for_interval)
async def process_interval(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Please enter a valid number (minutes).")
        return
    
    val = int(message.text)
    if val < MIN_MESSAGE_INTERVAL_MINUTES:
        await message.answer(f"❌ Interval must be at least {MIN_MESSAGE_INTERVAL_MINUTES} minutes.")
        return
    
    async with AsyncSessionLocal() as db:
        settings = await get_user_settings(db, message.from_user.id)
        settings.interval_minutes = val
        await db.commit()
    
    await message.answer(
        f"✅ Interval set to **{val} minutes**.",
        reply_markup=back_home_kb()
    )
    await state.clear()
