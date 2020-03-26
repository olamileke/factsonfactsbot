import re
from telegram.ext import BaseFilter


# Checking if the user has sent a link
class UrlFilter(BaseFilter):
    def filter(self, message):
        url_match = re.compile('.*http.*')

        if url_match.match(message.text) is None:
            return False

        return True
