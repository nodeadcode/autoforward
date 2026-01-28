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
            f"❉ **MANAGE GROUPS** ❉\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"◈ **Limit**: `{len(groups_list)}/{MAX_GROUPS_PER_USER}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"◈ `◈` = Enabled | `◊` = Disabled\n"
            f"⊹ Click a group name to toggle.\n"
            f"⊹ Click `🗑` to remove.",
            reply_markup=groups_kb(groups_list)
        )

@router.callback_query(F.data == "add_group")
async def cb_add_group(callback: types.CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as db:
        from database.models import User
        from sqlalchemy.future import select
        from database.crud import is_plan_active
        if not await is_plan_active(db, callback.from_user.id):
            await callback.answer("❌ Your plan has expired. Please redeem a code to continue.", show_alert=True)
            return

        from database.models import Session
        res = await db.execute(select(Session).where(Session.user_id == callback.from_user.id))
        session = res.scalar_one_or_none()
        
        if not (session and session.is_active):
            await callback.answer("❌ You must connect your Telegram account first!", show_alert=True)
            return

        groups_list = await get_user_groups(db, callback.from_user.id)
        if len(groups_list) >= MAX_GROUPS_PER_USER:
            await callback.answer("❌ You have reached the maximum group limit.", show_alert=True)
            return

    await callback.message.edit_text(
        "❉ **ADD NEW GROUP** ❉\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⊹ Send **Group ID** (e.g. `-100...`)\n"
        "⊹ OR **Group Username** (e.g. `@group`)\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "◊ **Note**: You must be a member of the group.",
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

@router.callback_query(F.data.startswith("toggle_group_"))
async def cb_toggle_group(callback: types.CallbackQuery):
    group_db_id = int(callback.data.split("_")[-1]) # This is the primary key 'id' from Group table
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Group).where(Group.id == group_db_id, Group.user_id == callback.from_user.id))
        group = result.scalar_one_or_none()
        if group:
            group.is_enabled = not group.is_enabled
            await db.commit()
            await callback.answer(f"Group {'enabled' if group.is_enabled else 'disabled'}.")
        else:
            await callback.answer("❌ Group not found.")
            
    await cb_groups(callback) # Refresh list

@router.callback_query(F.data.startswith("del_group_"))
async def cb_del_group(callback: types.CallbackQuery):
    # Keep delete functionality if they really want to remove it
    group_id_to_del = int(callback.data.split("_")[-1])
    
    async with AsyncSessionLocal() as db:
        await db.execute(delete(Group).where(Group.user_id == callback.from_user.id, Group.group_id == group_id_to_del))
        await db.commit()
    
    await callback.answer("🗑 Group removed.")
    await cb_groups(callback)
