import bs4


# test_template = ['tests/empik.html', 'tests/woblink.html']

# querry value -> text, decimal, url, img_url?

def prettyfie_me(html_tag_soup):
    def p_text(qs_text):
        if qs_text is None:
            return None
        return qs_text.get_text(strip=True)

    def p_decimal(qs_price):
        if qs_price is None:
            return None

        pretty_price = qs_price.find(text=True, recursive=False).getText(strip=True)
        if pretty_price.find(',') != -1:
            pretty_price = pretty_price.replace(',', '.')

        pretty_price = "".join(char for char in pretty_price if char.isdigit() or char == '.')
        return pretty_price

    def p_attr(qs_url, attr):
        if qs_url is None:
            return None

        return qs_url[attr]



    # ------------------------------------------------------------------------------------#

    ebooks = html_tag_soup.select_one('div.container.search-results.js-search-results'). \
        select('div.search-list-item')

    for ebook in ebooks:
        title = p_text(ebook.select_one('a.smartAuthor'))

        if ebook:
            price = p_decimal(ebook.select_one('.price.ta-price-tile'))
            img = p_attr(ebook.select_one('.lazy'), attr='lazy-img')
            url = p_attr(ebook.select_one('.seoTitle'), attr='href')

            print(url)

            # img = ebook.select_one('.lazy')
            # print(img['lazy-img'])


test_template = ['tests/empik.html']
read_html = []

for template in test_template:
    with open(template) as f:
        x = f.read()
        read_html.append(x)

for html in read_html:
    bs = bs4.BeautifulSoup(html, 'lxml')
    prettyfie_me(bs)


class Empik:
    BOOKSTORE_URL = 'https://www.empik.com/audiobooki-i-ebooki,35,s?q='
    ALL_EBOOK_CONTAINER = 'div.container.search-results.js-search-results'
    EBOOK_CONTAINER = 'div.search-list-item'
    EBOOK_DETAIL = {
        # key / tuple (qs, extract to, optional => attr)
        'author': ('a.smartAuthor', 'text'),
        'title': ('.ta-product-title', 'text'),
        'price': ('.price.ta-price-tile', 'decimal'),
        'jpg': ('.lazy', 'attr', 'lazy-img')
    }

    def __init__(self, user_input):
        self.user_input = user_input
        self.bookstores_url = self.get_url()

    def get_url(self):
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '%20'.join(self.user_input.split())])
