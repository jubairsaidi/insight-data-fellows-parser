from collections import Counter
from dataclasses import dataclass, field
from urllib import request

from bs4 import BeautifulSoup
from tabulate import tabulate


@dataclass
class Person:
    name: str = ''
    company: str = ''

    @property
    def company_first_word(self):
        return self.company.split(' ', 1)[0]


@dataclass
class Persons:
    persons: list = field(default_factory=list)

    def add_person(self, person):
        self.persons.append(person)

    def company_counts(self):
        counter = Counter([
            self.company_map(person.company)
            for person
            in self.persons
        ])

        return counter.most_common()

    @property
    def ranked_company_counts(self):
        return [
            list((i,) + row)
            for (i, row)
            in enumerate(self.company_counts(), 1)
        ]

    def company_map(self, company_name):
        mapping = {
            'Aiirbnb': 'Airbnb',
            'Intel': 'Intel Corporation',
            'Schireson': 'Schireson Associates'
        }

        return mapping.get(company_name, company_name)


@dataclass
class InsightDataFellows:
    base_url: str = ''
    fellows: Persons = Persons()
    fellow_items: list = field(default_factory=list)

    def setup(self):
        self.parse_page_from_url(self.base_url)

    def parse_page_from_url(self, url):
        page = request.urlopen(url)
        page = BeautifulSoup(page, 'html.parser')

        fellow_items = page.select('div.fellow_item')

        for item in fellow_items:
            name = item.find('div', class_='fellow_name').text
            company = item.find('div', class_='fellow_company').text

            fellow = Person(name, company)

            self.fellows.add_person(fellow)

        self.get_next_page(page)

    def get_next_page(self, page):
        pagination = page.find('div', class_='w-pagination-wrapper').find('a', class_='w-pagination-next')

        if pagination:
            next_page_link = pagination['href']
            next_page_url = self.base_url + next_page_link
            self.parse_page_from_url(next_page_url)

    def tabulate_company_counts(self):
        headers = ['rank', 'company', 'person_count']
        self.tabulate(headers, self.fellows.ranked_company_counts)

    def tabulate(self, headers=[], items=[]):
        print(tabulate(
            items,
            headers=headers,
            tablefmt='orgtbl'
        ))


# Lets use it!
url = 'https://www.insightdatascience.com/fellows'

parser = InsightDataFellows(url)

parser.setup()

parser.tabulate_company_counts()
