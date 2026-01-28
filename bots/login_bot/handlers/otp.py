from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from bots.login_bot.handlers.start import LoginStates
from bots.login_bot.session_manager import get_client, remove_client
from database.db import AsyncSessionLocal
from database.crud import get_or_create_user
from database.models import Session
from sqlalchemy.future import select
from bots.login_bot.keyboards.inline import otp_keyboard
from config.settings import BOT_TOKEN_MAIN
from aiogram import Bot

router = Router()

async def finish_login(message: types.Message, state: FSMContext, code: str, user_id: int):
    data = await state.get_data()
    phone = data.get("phone")
    phone_code_hash = data.get("phone_code_hash")
    api_id = data.get("api_id")
    api_hash = data.get("api_hash")
    
    client = get_client(user_id)
    if not client:
        await message.answer("❌ Session expired. Please /start again.")
        await state.clear()
        return

    msg = await message.answer("🔄 Verifying code...") if isinstance(message, types.Message) else await message.message.answer("🔄 Verifying code...")
    # If using callback, message is CallbackQuery, but we passed message object or we use callback.message
    # Standardize:
    # If caller passed a Message, answer it.
    
    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        
        session_file = f"bots/login_bot/sessions/{user_id}"
        
        async with AsyncSessionLocal() as db:
            await get_or_create_user(db, user_id, message.from_user.username)
            
            result = await db.execute(select(Session).where(Session.user_id == user_id))
            existing_session = result.scalar_one_or_none()
            
            if existing_session:
                existing_session.session_path = session_file
                existing_session.phone_number = phone
                existing_session.api_id = api_id
                existing_session.api_hash = api_hash
                existing_session.is_active = True
            else:
                new_session = Session(
                    user_id=user_id, 
                    session_path=session_file, 
                    phone_number=phone, 
                    api_id=api_id,
                    api_hash=api_hash,
                    is_active=True
                )
                db.add(new_session)
            
            await db.commit()
            
        # Notify Main Bot
        try:
            main_bot = Bot(token=BOT_TOKEN_MAIN)
            await main_bot.send_message(
                user_id,
                "✅ **LOGIN SUCCESSFUL**\n\n"
                "Your account has been connected to Spinify Ads.\n"
                "You can now manage your groups and scheduler in this bot."
            )
            await main_bot.session.close()
        except Exception as e:
            logger.error(f"Failed to notify main bot: {e}")

        await msg.edit_text(
            "❉ **LOGIN SUCCESSFUL** ❉\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "◈ Account linked successfully.\n"
            "◈ You can now close this bot and\n"
            "◈ Go back to the **Main Bot**.\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await client.disconnect()
        await remove_client(user_id)
        await state.clear()

    except PhoneCodeInvalidError:
        attempts = data.get("otp_attempts", 0) + 1
        if attempts >= 3:
            await msg.edit_text("❌ Too many wrong attempts. Session terminated. Please /start again.")
            await client.disconnect()
            await remove_client(user_id)
            await state.clear()
        else:
            await state.update_data(otp_attempts=attempts)
            await msg.edit_text(f"◊ **ERROR**: Invalid Code.\n⊹ Please try again. (Attempt {attempts}/3)")
    except SessionPasswordNeededError:
        await msg.edit_text("◊ **ERROR**: 2FA Password required.\n⊹ Please disable it temporarily or check terminal console if possible.", reply_markup=None)
        await client.disconnect()
        await remove_client(user_id)
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")
        await client.disconnect()
        await remove_client(user_id)
        await state.clear()

@router.message(LoginStates.waiting_for_otp)
async def process_otp_message(message: types.Message, state: FSMContext):
    code = message.text.replace(" ", "")
    if not code.isdigit():
        await message.answer("❌ Code must be a number.", reply_markup=otp_keyboard())
        return
    await finish_login(message, state, code, message.from_user.id)

@router.callback_query(F.data.startswith("otp_"))
async def process_otp_callback(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    data = await state.get_data()
    current_code = data.get("otp_input", "")

    if action == "submit":
        if not current_code:
            await callback.answer("❌ Enter code first!")
            return
        await callback.message.delete()
        await finish_login(callback, state, current_code, callback.from_user.id)
        return

    if action == "del":
        current_code = current_code[:-1]
    else:
        # Number
        if len(current_code) < 6: # Max OTP length usually 5 or 6
            current_code += action
    
    await state.update_data(otp_input=current_code)
    
    # Update message text
    display_code = " ".join(list(current_code)) if current_code else "..."
    text = (
        f"❉ **OTP ENTRY** ❉\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ **Entered**: `{display_code}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⊹ Use the keypad or type it:"
    )
    
    try:
        await callback.message.edit_text(text, reply_markup=otp_keyboard())
    except Exception:
        pass # Ignore if content didn't change
    
    await callback.answer()
