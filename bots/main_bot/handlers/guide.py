from aiogram import Router, types, F
from bots.main_bot.keyboards.inline import back_home_kb

router = Router()

@router.callback_query(F.data == "guide")
async def cb_guide(callback: types.CallbackQuery):
    guide_text = (
        "❉ **HOW TO SET YOUR MESSAGES** ❉\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "The bot now supports **SEQUENTIAL ROTATION** of your ad messages.\n\n"
        "◈ **Step 1**: Open **Saved Messages** in your Telegram.\n"
        "◈ **Step 2**: Post or forward **multiple** ad messages.\n"
        "◈ **Step 3**: The bot will fetch them and send them one-by-one!\n\n"
        "⊹ **Example Cycle**:\n"
        "   - Interval 1: Sends Message #1\n"
        "   - Interval 2: Sends Message #2\n"
        "   - Interval 3: Sends Message #3\n"
        "   - ... then loops back to #1.\n\n"
        "◊ **Note**: It will keep the order from oldest to newest of your last 50 messages."
    )
    await callback.message.edit_text(guide_text, reply_markup=back_home_kb())
