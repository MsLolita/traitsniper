import asyncio
import json
import random

import pyuseragents

from utils import delay


class Twitter:
    def __init__(self, cookies: dict):
        self.tweet_cookies = cookies

        self.tweet_headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'referer': 'https://twitter.com/i/oauth2/authorize',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': pyuseragents.random(),
            'x-client-transaction-id': 'o1rr+6DE909lqnJI6YpC3g6ZnBN3pmE59D1H1JRmOplhMWcIIxCwQC6BbAlZPwV/q/ux0KP/kZhW5rKWQ/eYnOsaQ2P+og',
            'x-client-uuid': 'ad52516b-9fb1-4988-9250-b8c886e1bbd7',
            'x-csrf-token': self.tweet_cookies["ct0"],
            'x-twitter-active-user': 'yes',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-client-language': 'en',
        }

        self.session = None

    async def connect(self, url: str):
        self.tweet_headers["Referer"] = url
        connect_url = Twitter.refactor_url(url)

        auth_code = await self.get_auth_code(connect_url)
        await delay(3)
        result = await self.authorize(auth_code)

        return result["redirect_uri"]

    async def visit_front_connect_page(self, url: str):
        async with self.session.get(
                url,
                headers=self.tweet_headers,
                cookies=self.tweet_cookies
        ) as resp:
            res_json = await resp.text()
            return res_json

    @staticmethod
    def refactor_url(url: str):
        return url.replace("https://twitter.com/i/oauth2/authorize?", "https://twitter.com/i/api/2/oauth2/authorize?")

    async def get_auth_code(self, connect_url: str) -> str:
        async with self.session.get(
                connect_url,
                headers=self.tweet_headers,
                cookies=self.tweet_cookies
        ) as resp:
            res_json = await resp.json()
            return res_json["auth_code"]

    async def authorize(self, auth_code: str):
        url = 'https://twitter.com/i/api/2/oauth2/authorize'

        data = {
            'approval': 'true',
            'code': auth_code,
        }

        async with self.session.post(
                url,
                data=data,
                headers=self.tweet_headers,
                cookies=self.tweet_cookies
        ) as resp:
            res_json = await resp.json()
            return res_json
