#

"""
"""

from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup, Tag
import requests

from .exchange_models import ExchangeMostTradedRow
from .util import convert_number


class ExchangePage:
    """
    """

    def __init__(self):
        """
        """
        self.__host = 'http://services.runescape.com'
        self.__session = requests.Session()

    def __get(self, path: str, **params) -> BeautifulSoup:
        """
        """
        url = urljoin(self.__host, path)
        res = self.__session.get(url)

        soup = BeautifulSoup(res.text, 'html.parser')
        # TODO: error handling
        return soup


    def most_traded(self):
        """
        """
        path = '/m=itemdb_rs/top100'
        params = {'list': 0}

        soup = self.__get(path, **params)
        rows = soup.select('.content > table > tbody > tr')
        data = []

        for row in rows:
            cells = [cell for cell in row.children if isinstance(cell, Tag)]

            href = urlparse(cells[0].a['href'])
            query = parse_qs(href.query)

            data.append(ExchangeMostTradedRow(
                id=query['obj'][0],
                name=cells[0].a.span.text,
                members=cells[1]['class'][0] == 'memberItem',
                min=cells[2].a.text,
                max=cells[3].a.text,
                median=cells[4].a.text,
                total=cells[5].a.text,
            ))

        return data


