import pyuseragents
import aiohttp
from aiohttp_proxy import ProxyConnector

from exceptions import LoginError
from socials import Twitter
from utils import delay, str_to_file, logger

from utils import Web3Utils


class TraitSniper(Twitter, Web3Utils):
    ref_code = ''

    def __init__(self, twitter_cookies: dict, key: str, proxy: str = None):
        Twitter.__init__(self, twitter_cookies)
        Web3Utils.__init__(self, key=key)

        self.proxy = f"http://{proxy}" if proxy else None

        self.address = None
        self.email = None

        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Referer': 'https://www.traitsnipergame.com/login?redirect=/earn',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': pyuseragents.random(),
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.session = aiohttp.ClientSession(connector=ProxyConnector.from_url(self.proxy) if self.proxy else None)

    async def link_twitter(self):
        try:
            await delay(2)
            url = await self.get_authorize_url()
            await delay(1)
            verify_connection_link = await self.connect(url)
            await delay(1)
            result = await self.__verify_twitter_connection(verify_connection_link)
            if result[0] == "" and result[1] == 302:
                # logger.info("Twitter linked")
                return True

        except Exception as e:
            logger.error(f"Error can't link twitter | {e}")
            return False

    async def __verify_twitter_connection(self, verify_connection_link: str):
        async with self.session.get(verify_connection_link, headers=self.headers,
                                    allow_redirects=False) as resp:
            return await resp.text(), resp.status

    async def get_sign_msg(self):
        url = 'https://www.traitsnipergame.com/api/sign'

        params = {
            'address': self.acct.address,
        }

        async with self.session.get(url, params=params,
                                    headers=self.headers) as resp:

            return await resp.text()

    async def login(self):
        await delay(2)
        url = 'https://www.traitsnipergame.com/api/login'

        msg = await self.get_sign_msg()

        json_data = {
            'address': self.acct.address,
            'inviteCode': self.ref_code,
            'sign': self.get_signed_code(msg),
            'source': 'metamask',
        }

        async with self.session.post(url, headers=self.headers, json=json_data) as resp:
            raw_json = await resp.json()

            if raw_json.get('token') is not None:
                self.set_auth_token(raw_json['token'])
                # logger.success(f"Login {self.acct.address}")
                return raw_json

        raise LoginError(f"Login error: {raw_json['msg']}")

    async def get_authorize_url(self):
        url = 'https://www.traitsnipergame.com/api/twitter/auth'

        params = {
            "callback": "https://www.traitsnipergame.com/earn"
        }

        async with self.session.get(url, params=params, headers=self.headers) as resp:
            raw_json = await resp.json()
            return raw_json['authUsl']

    async def close(self):
        await self.session.close()

    def set_auth_token(self, token: str):
        self.headers['authorization'] = f"Bearer {token}"
        self.session.cookie_jar.update_cookies({"Admin-Token": token})

    def logs(self, success: bool = True, msg: str = ""):
        file_msg = f"{self.acct.address}|{self.acct.key.hex()}"

        if success:
            str_to_file(f"data\\logs\\success.txt", file_msg)
            logger.success(f"Account {self.acct.address}")
        else:
            file_msg += f"|{msg}"
            str_to_file(f"data\\logs\\fail.txt", file_msg)
            logger.error(f"Failed {self.acct.address}")


