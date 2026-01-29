from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from telethon import TelegramClient
from bots.login_bot.handlers.start import LoginStates
from bots.login_bot.keyboards.inline import otp_keyboard
from bots.login_bot.session_manager import add_client, remove_client

router = Router()

@router.message(LoginStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip().replace(" ", "").replace("-", "")
    
    if not phone.startswith("+") or len(phone) < 7:
        await message.answer("◊ **ERROR**: Invalid phone format.\n⊹ Must start with `+` and include country code.")
        return
    
    if not phone[1:].isdigit():
        await message.answer("❌ Invalid format. Phone must contain only digits after +. Please try again:")
        return

    data = await state.get_data()
    api_id = data.get("api_id")
    api_hash = data.get("api_hash")
    user_id = message.from_user.id

    msg = await message.answer("❉ **GENERATING CODE** ❉\n━━━━━━━━━━━━━━━━━━━━\n⊹ Please wait...")

    # Initialize Telethon Client with file-based session
    session_file = f"sessions/user_{user_id}"
    client = TelegramClient(session_file, api_id, api_hash)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            send_code = await client.send_code_request(phone)
            
            # Store client and hash
            add_client(user_id, client)
            await state.update_data(phone=phone, phone_code_hash=send_code.phone_code_hash)
            
            await msg.edit_text(
            f"❉ **OTP SENT** ❉\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"◈ Code sent to: `{phone}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⊹ Use the keypad or type it:",
            reply_markup=otp_keyboard()
        )
            await state.set_state(LoginStates.waiting_for_otp)
        else:
            await msg.edit_text("⚠️ This account is already authorized.")
            await client.disconnect()
            
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}\n\nPlease /start and try again.")
        await remove_client(user_id)
