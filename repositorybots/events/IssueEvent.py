from abc import ABC, abstractmethod

class IssueEvent(ABC):

    @property
    @abstractmethod
    def github_conn(self):
        pass

    @property
    @abstractmethod
    def event_body(self):
        pass

    @abstractmethod
    def get_pull_request_author(self):
        pass

    @abstractmethod
    def add_comment(self, comment_body):
        pass

    @abstractmethod
    def add_label(self, label_name):
        pass


