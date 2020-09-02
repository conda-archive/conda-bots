from gidgethub import routing
from aiohttp import web
from ..bots import Librarian, ClaBot
from ..events.OpenedPullRequest import OpenedPullRequest
from ..events.IssueComment import IssueComment

summon_router = routing.Router()

@summon_router.register("issue_comment", action="created")
async def respond_to_summons(event, gh, bot_name, *args, **kwargs):
    issue_comment_event = IssueComment(gh, event)
    librarian = Librarian.Librarian(bot_name, issue_comment_event)
    claBot = ClaBot.ClaBot(bot_name, gh, issue_comment_event)
    comment_body = issue_comment_event.comment_body
    user_help_match = librarian.has_been_summoned(comment_body)
    cla_check_match = claBot.has_been_summoned(comment_body)
    if user_help_match:
        await librarian.check_library(user_help_match)
    if cla_check_match:
        if issue_comment_event.is_pull_request_comment:
            await claBot.check_authorized_users()
        
    return web.Response(status=200)

@summon_router.register("pull_request", action="opened")
async def check_cla_on_new_pr(event, gh, bot_name, *args, **kwargs):
    pull_request_event = OpenedPullRequest(gh, event)
    claBot = ClaBot.ClaBot(bot_name, gh, pull_request_event)
    await claBot.check_authorized_users()
    return web.Response(status=200)
