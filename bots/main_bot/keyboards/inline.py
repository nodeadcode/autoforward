from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb(user_id):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="❉ STATUS & STATS", callback_data="stats"))
    kb.row(
        InlineKeyboardButton(text="⊹ MANAGE GROUPS", callback_data="groups"),
        InlineKeyboardButton(text="◈ SETTINGS", callback_data="settings")
    )
    kb.row(InlineKeyboardButton(text="👤 MANAGE ACCOUNT", callback_data="account"))
    kb.row(
        InlineKeyboardButton(text="💎 MY PLAN", callback_data="plan"),
        InlineKeyboardButton(text="🎁 REDEEM CODE", callback_data="redeem")
    )
    kb.row(InlineKeyboardButton(text="📖 USER GUIDE", callback_data="guide"))
    kb.row(InlineKeyboardButton(text="⚡ FORCE SYNC", callback_data="sync"))
    return kb.as_markup()

def settings_kb(night_mode: bool, active: bool):
    kb = InlineKeyboardBuilder()
    
    night_status = "◈ ON" if night_mode else "◊ OFF"
    active_status = "◈ RUNNING" if active else "⏸ PAUSED"
    
    kb.row(InlineKeyboardButton(text=f"🌙 NIGHT MODE: {night_status}", callback_data="toggle_night"))
    kb.row(InlineKeyboardButton(text=f"◈ SCHEDULER: {active_status}", callback_data="toggle_active"))
    kb.row(InlineKeyboardButton(text="⏱ SET INTERVAL", callback_data="set_interval"))
    kb.row(InlineKeyboardButton(text="⬅ BACK", callback_data="home"))
    return kb.as_markup()

def groups_kb(groups: list):
    kb = InlineKeyboardBuilder()
    for group in groups:
        status_sym = "◈" if group.is_enabled else "◊"
        kb.row(
            InlineKeyboardButton(text=f"{status_sym} {group.group_name}", callback_data=f"toggle_group_{group.id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"del_group_{group.group_id}")
        )
    
    if len(groups) < 10:
        kb.row(InlineKeyboardButton(text="⊹ ADD GROUP", callback_data="add_group"))
    
    kb.row(InlineKeyboardButton(text="⬅ BACK", callback_data="home"))
    return kb.as_markup()

def account_kb(is_connected: bool):
    kb = InlineKeyboardBuilder()
    if is_connected:
        kb.row(InlineKeyboardButton(text="⌧ REMOVE ACCOUNT", callback_data="remove_account"))
    else:
        kb.row(InlineKeyboardButton(text="🔗 LOGIN VIA BOT", url="https://t.me/SpinifyLoginBot"))
        
    kb.row(InlineKeyboardButton(text="⬅ BACK", callback_data="home"))
    return kb.as_markup()

def back_home_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="⬅ BACK TO MENU", callback_data="home"))
    return kb.as_markup()
