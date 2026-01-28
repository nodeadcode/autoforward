from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def otp_keyboard():
    kb = InlineKeyboardBuilder()
    
    # 1 2 3
    kb.row(
        InlineKeyboardButton(text="1", callback_data="otp_1"),
        InlineKeyboardButton(text="2", callback_data="otp_2"),
        InlineKeyboardButton(text="3", callback_data="otp_3")
    )
    # 4 5 6
    kb.row(
        InlineKeyboardButton(text="4", callback_data="otp_4"),
        InlineKeyboardButton(text="5", callback_data="otp_5"),
        InlineKeyboardButton(text="6", callback_data="otp_6")
    )
    # 7 8 9
    kb.row(
        InlineKeyboardButton(text="7", callback_data="otp_7"),
        InlineKeyboardButton(text="8", callback_data="otp_8"),
        InlineKeyboardButton(text="9", callback_data="otp_9")
    )
    # < 0 OK
    kb.row(
        InlineKeyboardButton(text="⬅️", callback_data="otp_del"),
        InlineKeyboardButton(text="0", callback_data="otp_0"),
        InlineKeyboardButton(text="✅ Submit", callback_data="otp_submit")
    )
    
    return kb.as_markup()
