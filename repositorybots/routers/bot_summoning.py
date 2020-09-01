from gidgethub import routing
from aiohttp import web

summon_router = routing.Router()

# TODO this is overkill too
async def respond_to_help_request(gh, librarian, comment_url, user_help_match):
    message = librarian.check_library(user_help_match)
    if message:
        await gh.post(
            comment_url,
            data={ 'body': message }
        )
    return web.Response(status=200)

# TODO this is overkill.
async def respond_to_cla_check_request(gh, claBot, author, label_url, statuses_url, should_send_welcome_msg=False, comment_url=None):
    await claBot.check_authorized_users(gh, author, label_url, statuses_url, should_send_welcome_msg, comment_url)
    return web.Response(status=200)


@summon_router.register("issue_comment", action="created")
async def respond_to_summons(event, gh, librarian, claBot, *args, **kwargs):
    comment_url = event.data.get('issue').get('comments_url')
    comment_body = event.data.get('comment').get('body')
    user_help_match = librarian.has_been_summoned(comment_body)
    cla_check_match = claBot.has_been_summoned(comment_body)
    if user_help_match:
        await respond_to_help_request(gh, librarian, comment_url, user_help_match)
    elif cla_check_match:
        is_pull_request = event.data.get('issue').get('pull_request')
        if is_pull_request:
            issue = event.data.get('issue', {})
            pr_url = issue.get('pull_request').get('url')
            pr_res = await gh.getitem(pr_url)
            label_url = issue.get('labels_url')
            pr_content = pr_res
            author = pr_content.get('user').get('login')
            statuses_url = pr_content.get('statuses_url')
            await respond_to_cla_check_request(gh, claBot, author, label_url, statuses_url)
        
    return web.Response(status=200)

@summon_router.register("pull_request", action="opened")
async def check_cla_on_new_pr(event, gh, claBot, *args, **kwargs):
    pull_request = event.data.get('pull_request')
    user = pull_request.get('user')
    author = user.get('login')
    issue_url = pull_request.get('issue_url')
    issue_info = await gh.getitem(issue_url)
    label_url = issue_info.get('labels_url')
    status_url = pull_request.get('statuses_url')
    comment_url = pull_request.get('comments_url')
    await respond_to_cla_check_request(gh, claBot, author, label_url, status_url, should_send_welcome_msg=True, comment_url=comment_url)
