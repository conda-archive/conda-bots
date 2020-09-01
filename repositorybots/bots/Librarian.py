import yaml
import re
from .SummonableBot import SummonableBot

class Librarian(SummonableBot):

    def __init__(self, bot_name):
        self.help_command = 'help'
        self.help_preamble = "Here are my available responses"
        with open('./responses.yml') as file:
            response_list = yaml.load(file, Loader=yaml.FullLoader)
            available_responses = response_list.get('responses').keys()
            regex_for_responses = "\\s*|".join(available_responses)
            self.summoning_regex = r'(@' + bot_name + r')\s*' + f'({regex_for_responses}\\s*|{self.help_command})'

    def has_been_summoned(self, comment_body):
        return re.search(self.summoning_regex, comment_body, re.MULTILINE)

    def __prepare_new_issue_text(self, top_message, links):
        s = top_message + """\n\n- """
        s += "\n- ".join('['+ l.get('title') + '](' + l.get('url') +')' for l in links)
        return s

    def __prepare_help_response(self, top_message, responses):
        s = top_message + """:\n\n- """
        s += "\n- ".join(response for response in responses)
        return s

    def check_library(self, user_help_match):
        message = None
        with open('./responses.yml') as file:
            response_list = yaml.load(file, Loader=yaml.FullLoader)
            response_to_fetch = user_help_match.group(2).strip()

            if response_to_fetch == self.help_command:
                message = self.__prepare_help_response(
                    self.help_preamble, response_list.get('responses').keys())
            else:
                requested_response = response_list.get('responses').get(response_to_fetch, '')
                message = self.__prepare_new_issue_text(
                    requested_response.get('message', ''), requested_response.get('helpful_links', []))
        return message
