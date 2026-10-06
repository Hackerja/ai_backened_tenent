import asyncio
from .security import get_user


async def main():
    print(await get_user("kash@gmail.com"))

asyncio.run(main())