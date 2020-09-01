import re
import json
from .SummonableBot import SummonableBot

class ClaBot(SummonableBot):
    def __init__(self, bot_name):
        self.summoning_regex = r'(@' + bot_name + r')\s*(check)'

    def has_been_summoned(self, comment_body):
        return re.search(self.summoning_regex, comment_body, re.MULTILINE)

    async def retrieve_cla_config(self, gh):
        accepted_signers_url = 'https://api.github.com/repos/conda/clabot-config/contents/.clabot'

        accepted_signers_res = await gh.getitem(
            accepted_signers_url,
            accept='application/vnd.github.VERSION.raw'
        )
        accepted_signers_config = json.loads(accepted_signers_res)

        return accepted_signers_config

    async def check_authorized_users(self, gh, author, label_url, statuses_url, should_send_welcome_msg=False, comment_url=None):
        accepted_signers_config = await self.retrieve_cla_config(gh)
        accepted_signers = accepted_signers_config["contributors"]
        if author in accepted_signers:
            await gh.post(
                label_url,
                data={ 'labels': ['cla-signed'] }
            )
            pr_state = 'success'
        else:
            pr_state = 'failure'
            if should_send_welcome_msg and comment_url:
                message = accepted_signers_config.get("message", 'No Message Provided')
                await gh.post(
                    comment_url,
                    data={ 'body': message }
                )
        await gh.post(
            statuses_url,
            data={ 'context': 'verification/cla-signed', 'state': pr_state }
        )
        return
