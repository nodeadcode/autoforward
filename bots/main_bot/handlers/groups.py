from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import delete
from database.db import AsyncSessionLocal
from database.crud import get_user_groups, add_group
from database.models import Group
from bots.main_bot.keyboards.inline import groups_kb, back_home_kb
from config.settings import MAX_GROUPS_PER_USER

router = Router()

class GroupStates(StatesGroup):
    waiting_for_group_id = State()

@router.callback_query(F.data == "groups")
async def cb_groups(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with AsyncSessionLocal() as db:
        groups_list = await get_user_groups(db, user_id)
        
        await callback.message.edit_text(
            f"👥 **Manage Groups ({len(groups_list)}/{MAX_GROUPS_PER_USER})**\n\n"
            "Click on a group to DELETE it.\n"
            "Click 'Add Group' to add a new one.",
            reply_markup=groups_kb(groups_list)
        )

@router.callback_query(F.data == "add_group")
async def cb_add_group(callback: types.CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as db:
        groups_list = await get_user_groups(db, callback.from_user.id)
        if len(groups_list) >= MAX_GROUPS_PER_USER:
            await callback.answer("❌ You have reached the maximum group limit.", show_alert=True)
            return

    await callback.message.edit_text(
        "➕ **Add Group**\n\n"
        "Please send the **Group ID** (e.g., -100123456789) OR **Group Username** (e.g., @mygroup).\n\n"
        "Note: You (your user account) must be a member of this group.",
        reply_markup=back_home_kb()
    )
    await state.set_state(GroupStates.waiting_for_group_id)

@router.message(GroupStates.waiting_for_group_id)
async def process_group_id(message: types.Message, state: FSMContext):
    txt = message.text.strip()
    
    if not (txt.startswith("@") or txt.startswith("-") or txt.isdigit()):
        await message.answer("❌ Invalid format. Please send a valid Group ID or Username.")
        return
    
    # Heuristic check for integer ID
    group_id_int = 0
    group_name = txt
    
    # We might need to resolve username to ID, but MainBot can't do that easily if it's not in the group.
    # We will save what the user gave us. The WORKER will handle resolution errors.
    # If the user gave an integer ID:
    if txt.replace("-", "").isdigit():
        group_id_int = int(txt)
    else:
        # It's a username. We can't really get ID without being in it or using Telegram API userbot.
        # So we'll save the "group_id" field as 0 for now and store the string in "group_name" or handle this better.
        # Actually, models.py has `group_id = Column(BigInteger)` which expects int.
        # WE NEED INT.
        # If user sends username, we can't save it in BigInteger column easily unless we resolve it.
        # MainBot is a bot. If user sends @group, MainBot can try `get_chat("@group")`.
        try:
            chat = await message.bot.get_chat(txt)
            group_id_int = chat.id
            group_name = chat.title
        except Exception as e:
            await message.answer(f"❌ Could not find group '{txt}'. ensure the bot is added or use the numeric ID.\nError: {e}")
            return

    async with AsyncSessionLocal() as db:
        # ID duplicacy check
        g_list = await get_user_groups(db, message.from_user.id)
        if any(g.group_id == group_id_int for g in g_list):
             await message.answer("⚠️ This group is already added.")
             await state.clear()
             return

        await add_group(db, message.from_user.id, group_id_int, group_name)
    
    await message.answer(f"✅ Group **{group_name}** added!", reply_markup=back_home_kb())
    await state.clear()

@router.callback_query(F.data.startswith("del_group_"))
async def cb_del_group(callback: types.CallbackQuery):
    group_id_to_del = int(callback.data.split("_")[-1])
    
    async with AsyncSessionLocal() as db:
        await db.execute(delete(Group).where(Group.user_id == callback.from_user.id, Group.group_id == group_id_to_del))
        await db.commit()
    
    await callback.answer("🗑 Group removed.")
    await cb_groups(callback) # Refresh list
