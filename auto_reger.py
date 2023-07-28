import asyncio
import traceback

from exceptions import LoginError
from utils import logger
from utils.auto_generate.emails import generate_random_emails
from utils.auto_generate.wallets import generate_random_wallets
from utils.file_manager import (
    shift_file,
    file_to_list
)

from trait_sniper import TraitSniper
from utils.cookies_manager import CookiesManager


class AutoReger:
    def __init__(self):
        self.emails_path: str = "data\\inputs\\emails.txt"
        self.proxies_path: str = "data\\inputs\\proxies.txt"
        self.wallets_path: str = "data\\inputs\\wallets.txt"
        self.twitter_cookies_path: str = "data\\inputs\\twitter_cookies.txt"

        self.success = 0

    def get_accounts(self):
        emails = file_to_list(self.emails_path)
        wallets = file_to_list(self.wallets_path)
        proxies = file_to_list(self.proxies_path)
        twitter_cookies = CookiesManager(self.twitter_cookies_path).get_cookies()

        min_accounts_len = len(twitter_cookies)

        if not twitter_cookies:
            logger.error("No twitter tweet_cookies in file!")
            return

        # if proxies or len(proxies) < min_accounts_len:
        #     logger.error("Not enough proxies!")
        #     return

        if not emails:
            logger.info(f"Generated random emails!")
            emails = generate_random_emails(min_accounts_len)

        if not wallets:
            logger.info(f"Generated random wallets!")
            wallets = [wallet[1] for wallet in generate_random_wallets(min_accounts_len)]

        accounts = []

        if len(emails) < len(wallets):
            for i in range(len(emails)):
                accounts.append((emails[i], wallets[i], proxies[i] if len(proxies) > i else None, twitter_cookies[i]))
        else:
            for i in range(len(wallets)):
                accounts.append((emails[i], wallets[i], proxies[i] if len(proxies) > i else None, twitter_cookies[i]))

        return accounts

    def remove_account(self):
        return shift_file(self.emails_path), shift_file(self.wallets_path), \
            shift_file(self.proxies_path), shift_file(self.twitter_cookies_path)

    async def start(self):
        referral_link = input("Referral link(https://www.traitsnipergame.com/earn?inviteCode=deBVy): ")

        TraitSniper.ref_code = referral_link.split('?inviteCode=')[-1]

        # mobile_proxy = input("Mobile proxy(press Enter if not need):")
        #
        # if mobile_proxy:
        #     mobile_proxy_change_ip = input("Mobile proxy change ip link:")
        #
        #     if not mobile_proxy_change_ip:
        #         logger.error(f"Provide mobile proxy change ip link")
        #         return

        custom_user_delay = float(input("Delay(in seconds): "))

        accounts = self.get_accounts()

        if not accounts:
            return

        for account in accounts:
            await asyncio.sleep(custom_user_delay)
            await self.register(account)

        if self.success:
            logger.success(f"Successfully registered {self.success} accounts :)")
        else:
            logger.warning(f"No accounts registered :(")

    async def register(self, account: tuple):
        email, key, proxy, twitter_cookies = account
        trait_sniper = TraitSniper(twitter_cookies, key, proxy)

        is_ok = False
        crash_error: str = ""

        try:
            await trait_sniper.login()
            is_ok = await trait_sniper.link_twitter()
            # await asyncio.sleep(20)
            await trait_sniper.close()
        except LoginError as e:
            crash_error = str(e)
            logger.error(f"Login error {crash_error}")
        except Exception as e:
            crash_error = str(e)
            logger.error(f"Global error {crash_error} {traceback.format_exc()}")

        self.remove_account()

        trait_sniper.logs(is_ok, crash_error)

        if is_ok:
            self.success += 1

    @staticmethod
    def is_file_empty(path: str):
        return not open(path).read().strip()
