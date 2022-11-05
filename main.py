from typing import List
import json

import requests
from bs4 import BeautifulSoup


class NfjOffers:
    id: str
    name: str
    link: str
    city: str


def post_nfj() -> dict:
    # returns dict with lists
    headers = {
        "authority": "nofluffjobs.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "dnt": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    }

    params = {
        "limit": "10",
        "offset": "0",
        "salaryCurrency": "PLN",
        "salaryPeriod": "month",
        "region": "pl",
    }

    json_data = {
        "rawSearch": "city=remote,katowice,slask seniority=trainee,junior",
        "page": 1,
    }

    response = requests.post(
        "https://nofluffjobs.com/api/search/posting",
        params=params,
        headers=headers,
        json=json_data,
    )
    print(response.text)
    return response.json()


def sort_nfj(json_nfj: dict) -> List[NfjOffers]:
    # need to scrape info from dict.lists to NfjOffers
    q.get("postings")[1]
    pass


if __name__ == "__main__":
    q = post_nfj()
