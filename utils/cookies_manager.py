import json

from exceptions import CookiesParseError
from . import logger
from .file_manager import file_to_list


class CookiesManager:
    def __init__(self, file_name):
        self.file_name = file_name

    def get_cookies(self):
        try:
            raw_cookies = file_to_list(self.file_name)

            accounts_cookies = []
            for raw_cookie in raw_cookies:
                accounts_cookies.append(CookiesManager.__parse_cookies(json.loads(raw_cookie)))

            return accounts_cookies
        except Exception as e:
            logger.error(f"Error when parse cookies: {e}")
            exit()

    @staticmethod
    def __parse_cookies(raw_cookies):
        cookies = {}
        for cookie in raw_cookies:
            cookies[cookie['name']] = cookie['value']
        return cookies

