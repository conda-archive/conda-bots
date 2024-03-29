import asyncio
import os
import sys
import traceback
import aiohttp
from aiohttp import web
import cachetools
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing
from gidgethub import sansio
from .bots import Librarian, ClaBot
from .routers.bot_summoning import summon_router

router = routing.Router(summon_router)
cache = cachetools.LRUCache(maxsize=500)

async def main(request):
    try:
        body = await request.read()
        secret = os.environ.get("GH_SECRET")
        event = sansio.Event.from_http(request.headers, body, secret=secret)
        oauth_token = os.environ.get("GH_AUTH")
        print('GH delivery ID', event.delivery_id, file=sys.stderr)
        if event.event == "ping":
            return web.Response(status=200)

        bot_name = os.environ.get("BOT_NAME")
        
        async with aiohttp.ClientSession() as session:
            gh = gh_aiohttp.GitHubAPI(session, bot_name,
                                      oauth_token=oauth_token,
                                      cache=cache)

            await asyncio.sleep(1)
            await router.dispatch(event, gh, bot_name, session=session)
        try:
            print('GH requests remaining:', gh.rate_limit.remaining)
        except AttributeError:
            pass
        return web.Response(status=200)
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        return web.Response(status=500)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/", main)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)
    web.run_app(app, port=port)