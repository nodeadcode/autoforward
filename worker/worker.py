import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.db import AsyncSessionLocal, init_db
from database.models import User, Session, Settings
from worker.sender import process_user
from config.settings import NIGHT_MODE_START, NIGHT_MODE_END

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Worker")

def is_night_time():
    now = datetime.now()
    # Simple check for 00:00 to 06:00
    # NIGHT_MODE_START = 0, NIGHT_MODE_END = 6
    return NIGHT_MODE_START <= now.hour < NIGHT_MODE_END

async def worker_loop():
    logger.info("Worker started.")
    await init_db()

    while True:
        try:
            async with AsyncSessionLocal() as db:
                # eager load session and groups and settings
                stmt = select(User).options(
                    selectinload(User.session),
                    selectinload(User.groups),
                    selectinload(User.settings)
                )
                result = await db.execute(stmt)
                users = result.scalars().all()

                current_time = datetime.utcnow()

                tasks = []
                for user in users:
                    # Check validity
                    if not user.session or not user.session.is_active:
                        continue
                    
                    if not user.settings or not user.settings.active:
                        continue

                    # Plan Expiry Check
                    if user.plan_expiry and user.plan_expiry < current_time:
                        continue # Plan expired

                    # Night Mode Check
                    if user.settings.night_mode_enabled and is_night_time():
                        continue

                    # Interval Check (DB Based Persistence)
                    last_run = user.settings.last_run
                    interval = timedelta(minutes=user.settings.interval_minutes)
                    
                    if last_run and (current_time - last_run) < interval:
                        continue

                    # If we passed all checks, queue the task
                    # Process User will handle updating the DB on success
                    tasks.append(process_user(user.id))

                if tasks:
                    logger.info(f"Processing {len(tasks)} active users...")
                    await asyncio.gather(*tasks)

            # Main loop check frequency
            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Worker Loop Error: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("Worker stopped.")
