from .IssueEvent import IssueEvent

class OpenedPullRequest(IssueEvent):

    def __init__(self, github_conn, event):
        self._github_conn = github_conn
        self._event_body = event.data
        self._associated_issue = None

    @property
    def github_conn(self):
        return self._github_conn

    @property
    def event_body(self):
        return self._event_body

    async def get_associated_issue(self):
        if not self._associated_issue:
            pr = self.event_body.get('pull_request', {})
            issue_url = pr.get('issue_url')
            if issue_url:
                issue_res = await self.github_conn.getitem(issue_url)
                self._associated_issue = issue_res
        return self._associated_issue

    async def get_pull_request_author(self):
        user = self.event_body['pull_request']['user']['login']
        return user

    async def add_label(self, label):
        issue_info = await self.get_associated_issue()
        label_url = issue_info.get('labels_url')
        await self.github_conn.post(
            label_url,
            data={ 'labels': [ label ] }
        )
    
    async def add_comment(self, comment_body):
        comment_url = self.event_body['pull_request']['comments_url']
        await self.github_conn.post(
            comment_url,
            data={ 'body': comment_body }
        )

    async def set_status(self, status_context, status):
        status_url = self.event_body['pull_request']['statuses_url']
        await self.github_conn.post(
            status_url,
            data={ 'context': status_context, 'state': status }
        )
