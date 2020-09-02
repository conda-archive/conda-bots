from .Event import Event

class IssueComment(Event):
    
    def __init__(self, github_conn, event):
        self._github_conn = github_conn
        self._event_body = event.data
        self._associated_pull_request = None

    @property
    def github_conn(self):
        return self._github_conn

    @property
    def event_body(self):
        return self._event_body

    @property
    def comment_body(self):
        return self.event_body.get('comment', {}).get('body', '')

    @property
    def is_pull_request_comment(self):
        return self.event_body.get('issue', {}).get('pull_request')

    async def get_associated_pull_request(self):
        if not self._associated_pull_request:
            issue = self.event_body.get('issue', {})
            pr_url = issue.get('pull_request').get('url')
            if pr_url:
                pr_res = await self.github_conn.getitem(pr_url)
                self._associated_pull_request = pr_res
        return self._associated_pull_request

    async def get_pull_request_author(self):
        pr_res = await self.get_associated_pull_request()
        author =  pr_res.get('user', {}).get('login', None)
        return author

    async def add_label(self, label):
        issue = self.event_body.get('issue', {})
        label_url = issue.get('labels_url')
        await self.github_conn.post(
            label_url,
            data={ 'labels': [ label ] }
        )
    
    async def add_comment(self, comment_body):
        issue = self.event_body.get('issue', {})
        comment_url = issue.get('comments_url')
        await self.github_conn.post(
            comment_url,
            data={ 'body': comment_body }
        )

    async def set_status(self, status_context, status):
        pr_res = await self.get_associated_pull_request()
        status_url = pr_res.get('statuses_url')
        await self.github_conn.post(
            status_url,
            data={ 'context': status_context, 'state': status }
        )
