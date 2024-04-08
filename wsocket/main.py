from wsConfig import start_websocket_server
import asyncio

async def main():
    await start_websocket_server()

if __name__ == "__main__":
    asyncio.run(main())
