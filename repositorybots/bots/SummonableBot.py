from abc import ABC, abstractmethod

class SummonableBot(ABC):

    @abstractmethod
    def has_been_summoned(self, comment_body):
        pass
