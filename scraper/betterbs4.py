import dataclasses
from dataclasses import dataclass
from decimal import Decimal

import bs4


# test_template = ['tests/empik.html', 'tests/woblink.html']

# querry value -> text, decimal, url, img_url?


class Empik:
    BOOKSTORE_URL = 'https://www.empik.com/audiobooki-i-ebooki,35,s?q='
    ALL_EBOOK_CONTAINER = 'div.container.search-results.js-search-results'
    EBOOK_CONTAINER = 'div.search-list-item'
    EBOOK_DETAILS = {
        'author': {'qs': 'a.smartAuthor', 'type': 'text'},
        'title': {'qs': '.ta-product-title', 'type': 'text'},
        'price': {'qs': '.price.ta-price-tile', 'type': 'decimal'},
        'jpg': {'qs': '.lazy', 'type': 'attribute', 'attr': 'lazy-img'},
        'url': {'qs': '.seoTitle', 'type': 'attribute', 'attr': 'href'}
    }

    def __init__(self, user_input):
        self.user_input = user_input
        self.bookstores_url = self.get_url()

    def get_url(self):
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '%20'.join(self.user_input.split())])


class Woblink:
    BOOKSTORE_URL = 'https://woblink.com/katalog/ebooki?szukasz='
    ALL_EBOOK_CONTAINER = 'ul.catalog-items.lista'
    EBOOK_CONTAINER = 'div [data-item-layout="tiles"]'
    EBOOK_DETAILS = {
        'author': {'qs': 'p.catalog-tile__author a', 'type': 'text'},
        'title': {'qs': 'a.catalog-tile__title span', 'type': 'text'},
        'price': {'qs': 'p.catalog-tile__new-price span', 'type': 'decimal'},
        'jpg': {'qs': '.lazy-animated', 'type': 'attribute', 'attr': 'srcset'},
        'url': {'qs': ".catalog-tile__title", 'type': 'attribute', 'attr': 'href'},
    }

    def __init__(self, user_input):
        self.user_input = user_input
        self.bookstores_url = self.get_url()

    def get_url(self):
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '+'.join(self.user_input.split())])


@dataclass
class Task(Woblink):
    owner_model_id: int
    user_input: str
    _: dataclasses.KW_ONLY
    data: dict = None
    url: str = None
    querry_selectors: dict = None
    email: bool = None
    email_price: Decimal = None

    def __post_init__(self):
        # In celery, this class is initiated without any inheritance, but in Task Manager he needs to be mixed with
        # any bookstore class. If mixed, we need to grab necessary class attribute as url or queryselectors because
        # we are using 'asdict' when passing this class as args to Celery Worker.
        if self.__class__.__base__ != object:
            super().__init__(self.user_input)
            self.url = self.bookstores_url
            self.querry_selectors = {
                'BOOKSTORE_URL': self.bookstores_url,
                'ALL_EBOOK_CONTAINER': self.ALL_EBOOK_CONTAINER,
                'EBOOK_CONTAINER': self.EBOOK_CONTAINER,
                'EBOOK_DETAILS': self.EBOOK_DETAILS
            }


def prettyfie_me(html_tag_soup, task):
    def p_text(qs):
        if qs is None:
            return None
        return qs.get_text(strip=True)

    def p_decimal(qs):
        if qs is None:
            return None

        pretty_price = qs.find(text=True, recursive=False).getText(strip=True)
        if pretty_price.find(',') != -1:
            pretty_price = pretty_price.replace(',', '.')

        pretty_price = "".join(char for char in pretty_price if char.isdigit() or char == '.')
        return pretty_price

    def p_attr(qs, attr):
        if qs is None:
            return None

        try:
            return qs[attr]
        except KeyError:
            return ''
    # ------------------------------------------------------------------------------------#

    ebooks = html_tag_soup.select_one(task.querry_selectors['ALL_EBOOK_CONTAINER']). \
        select(task.querry_selectors['EBOOK_CONTAINER'])


    scrap_result = {}

    for ebook in ebooks:
        test = ebook.select_one(task.querry_selectors['EBOOK_DETAILS']['title']['qs'])

        if test:
            for key, eb_detail in task.querry_selectors['EBOOK_DETAILS'].items():

                match eb_detail['type']:
                    case 'text':
                        value = p_text(ebook.select_one(eb_detail['qs']))
                    case 'decimal':
                        value = p_decimal(ebook.select_one(eb_detail['qs']))
                    case 'attribute':
                        value = p_attr(ebook.select_one(eb_detail['qs']), eb_detail['attr'])
                    case _:
                        value = None

                scrap_result.update({key: value})
            return

        # title = p_text(ebook.select_one(task.querry_selectors['EBOOK_DETAIL']['title']['qs']))
        # if title:
        #     title = p_text(ebook.select_one('a.smartAuthor'))
        #     # price = p_decimal(ebook.select_one('.price.ta-price-tile'))
        #     # img = p_attr(ebook.select_one('.lazy'), attr='lazy-img')
        #     # url = p_attr(ebook.select_one('.seoTitle'), attr='href')
        #
        #     print(repr(title))
        #     # print(repr(price))
        #     # print(repr(img))
        #     # print(repr(url))
        #     return


test_template = ['tests/woblink.html']
read_html = []

for template in test_template:
    with open(template) as f:
        x = f.read()
        read_html.append(x)

for html in read_html:
    bs = bs4.BeautifulSoup(html, 'lxml')
    test_task_object = Task('Maciej', '2')
    prettyfie_me(bs, test_task_object)

# print(test_task_object.querry_selectors)
