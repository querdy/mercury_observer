import asyncio
import aioschedule


def get_user_tasks(user_id: int):
    jobs = aioschedule.jobs
    user_tasks = [job for job in jobs if job.job_func.args[0]["from"]["id"] == user_id]
    return user_tasks


async def job_create(function, params=None):
    params = params or []
    aioschedule.every(1).minutes.do(function, *params)


async def run_scheduler(*args, **kwargs):
    async def run():
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

    asyncio.create_task(run())


def job_remove(user_tasks: list):
    [aioschedule.jobs.remove(task) for task in user_tasks]