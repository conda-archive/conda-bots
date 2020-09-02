import re
import json
from jinja2 import Template
from .SummonableBot import SummonableBot
from ..events.OpenedPullRequest import OpenedPullRequest

class ClaBot(SummonableBot):

    def __init__(self, bot_name, gh, event):
        self.summoning_regex = r'(@' + bot_name + r')\s*(check)'
        self.success_pr_label = 'cla-signed'
        self.pr_status_context = 'verification/cla-signed'
        self.accepted_signers_url = 'https://api.github.com/repos/conda/clabot-config/contents/.clabot'
        self.github_conn = gh
        self.event = event

    async def __mark_pull_request_signed(self):
        await self.event.add_label(self.success_pr_label)
    
    async def __comment_on_pull_request(self, message):
        await self.event.add_comment(message)
    
    async def __set_pull_request_status(self, status):
        await self.event.set_status(self.pr_status_context, status)

    async def __retrieve_cla_config(self):
        accepted_signers_res = await self.github_conn.getitem(
            self.accepted_signers_url,
            accept='application/vnd.github.VERSION.raw'
        )
        accepted_signers_config = json.loads(accepted_signers_res)

        return accepted_signers_config

    def has_been_summoned(self, comment_body):
        return re.search(self.summoning_regex, comment_body, re.MULTILINE)

    async def check_authorized_users(self):
        should_send_welcome_msg = isinstance(self.event, OpenedPullRequest)

        accepted_signers_config = await self.__retrieve_cla_config()
        accepted_signers = accepted_signers_config.get("contributors")
        author = await self.event.get_pull_request_author()
        if author in accepted_signers:
            await self.__mark_pull_request_signed()
            pr_state = 'success'
        else:
            pr_state = 'failure'
            if should_send_welcome_msg:
                message = accepted_signers_config.get("message", 'No Message Provided')
                rendered_message = Template(message).render(usersWithoutCLA=f"@{author}")
                await self.__comment_on_pull_request(rendered_message)
        await self.__set_pull_request_status(pr_state)
