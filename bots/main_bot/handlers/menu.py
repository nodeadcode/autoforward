from aiogram import Router, types, F
from bots.main_bot.keyboards.inline import main_menu_kb

router = Router()

# This file might be redundant if merged with start.py, 
# but useful for separating logic if "Menu" becomes complex.
# For now, start.py handles the main menu display so this acts as a receiver for specific stats logic if needed.

@router.callback_query(F.data == "stats")
async def cb_stats(callback: types.CallbackQuery):
    # TODO: Fetch real stats from DB
    await callback.answer("Fetching stats...", show_alert=False)
    
    # Mock stats
    stats_text = (
        "📊 **Your Statistics**\n\n"
        "🟢 **Status**: Running\n"
        "📅 **Plan Expires**: 2026-02-05\n"
        "👥 **Active Groups**: 3/10\n"
        "📨 **Messages Sent Today**: 42\n"
        "🌙 **Night Mode**: ON"
    )
    
    # We can add a "Back" button here
    from bots.main_bot.keyboards.inline import back_home_kb
    await callback.message.edit_text(stats_text, reply_markup=back_home_kb())
