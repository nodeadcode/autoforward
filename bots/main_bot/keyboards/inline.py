from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb(user_id):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📊 Status & Stats", callback_data="stats"))
    kb.row(
        InlineKeyboardButton(text="👥 Manage Groups", callback_data="groups"),
        InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")
    )
    kb.row(InlineKeyboardButton(text="👤 Manage Account", callback_data="account"))
    kb.row(
        InlineKeyboardButton(text="💎 My Plan", callback_data="plan"),
        InlineKeyboardButton(text="🎁 Redeem Code", callback_data="redeem")
    )
    kb.row(InlineKeyboardButton(text="🔄 Force Sync", callback_data="sync"))
    return kb.as_markup()

def settings_kb(night_mode: bool, active: bool):
    kb = InlineKeyboardBuilder()
    
    night_status = "✅ ON" if night_mode else "❌ OFF"
    active_status = "✅ RUNNING" if active else "⏸ PAUSED"
    
    kb.row(InlineKeyboardButton(text=f"🌙 Night Mode: {night_status}", callback_data="toggle_night"))
    kb.row(InlineKeyboardButton(text=f"🚀 Scheduler: {active_status}", callback_data="toggle_active"))
    kb.row(InlineKeyboardButton(text="⏱ Set Interval", callback_data="set_interval"))
    kb.row(InlineKeyboardButton(text="🔙 Back", callback_data="home"))
    return kb.as_markup()

def groups_kb(groups: list):
    kb = InlineKeyboardBuilder()
    for group in groups:
        kb.row(InlineKeyboardButton(text=f"🗑 {group.group_name}", callback_data=f"del_group_{group.group_id}"))
    
    if len(groups) < 10:
        kb.row(InlineKeyboardButton(text="➕ Add Group", callback_data="add_group"))
    
    kb.row(InlineKeyboardButton(text="🔙 Back", callback_data="home"))
    return kb.as_markup()

def back_home_kb():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔙 Back to Menu", callback_data="home"))
    return kb.as_markup()
