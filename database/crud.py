from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Settings, Session, Group, RedeemCode
from datetime import datetime, timedelta

async def get_or_create_user(db: AsyncSession, user_id: int, username: str = None):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        # Create user with default trial
        trial_expiry = datetime.utcnow() + timedelta(days=7)
        user = User(id=user_id, username=username, plan_expiry=trial_expiry)
        db.add(user)
        # Create default settings
        settings = Settings(user_id=user_id)
        db.add(settings)
        await db.commit()
    return user

async def get_user_settings(db: AsyncSession, user_id: int):
    result = await db.execute(select(Settings).where(Settings.user_id == user_id))
    return result.scalar_one_or_none()

async def add_group(db: AsyncSession, user_id: int, group_id: int, group_name: str):
    # Check limit? (Should be done in handler, but good to have safeguard)
    new_group = Group(user_id=user_id, group_id=group_id, group_name=group_name)
    db.add(new_group)
    await db.commit()
    return new_group

async def get_user_groups(db: AsyncSession, user_id: int):
    result = await db.execute(select(Group).where(Group.user_id == user_id))
    return result.scalars().all()

async def create_redeem_code(db: AsyncSession, code: str, duration: int):
    new_code = RedeemCode(code=code, duration_days=duration)
    db.add(new_code)
    await db.commit()
    return new_code

async def redeem_code(db: AsyncSession, user_id: int, code: str):
    result = await db.execute(select(RedeemCode).where(RedeemCode.code == code, RedeemCode.is_used == False))
    redeem_code = result.scalar_one_or_none()
    
    if redeem_code:
        redeem_code.is_used = True
        redeem_code.used_by = user_id
        
        # Extend user plan
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            current_expiry = user.plan_expiry if user.plan_expiry > datetime.utcnow() else datetime.utcnow()
            user.plan_expiry = current_expiry + timedelta(days=redeem_code.duration_days)
        
        await db.commit()
        return True
    return False
