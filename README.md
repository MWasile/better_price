
# Better Price

Better Price is a Django app that lets you search and compare e-book prices at any online bookstore. It is based on real-time web data scraping. 
## Tech Stack
AioHttp, Django, Celery, Redis, PostgreSQL, Channels, Django Rest Framework and Docker.


## Requirements
```bash
  Python 3.10 or higher 
  Docker
```

## Run 

Clone the project

```bash
  git clone https://github.com/MWasile/better_price
```

Go to the project directory

```bash
  cd better_price
```

Start the server

```bash
  docker compose up
```


## Usage/Examples

 ### Non-registered user:
  - Search for e-books.
 ### Registered user:
  - Search for e-books.
  - Visit Dashboard.
  - Check your search history.
  - Set email alert for a price based on user input.

## FAQ

#### How to add another bookstores?

Create your bookstores class in async_scraper.py

```python
class NewBookstores:
    BOOKSTORE_URL = '' # bookstores url
    ALL_EBOOK_CONTAINER = '' # queryselector to main container with e-books on page.
    EBOOK_CONTAINER = '' # queryselector to single e-book container
    EBOOK_DETAILS = {
      #example
        'author': {'qs': 'a.smartAuthor', 'type': 'text'},
        'title': {'qs': '.ta-product-title', 'type': 'text'},
        'price': {'qs': '.price.ta-price-tile', 'type': 'decimal'},
        'jpg': {'qs': '.lazy', 'type': 'attribute', 'attr': 'lazy-img'},
        'url': {'qs': '.seoTitle', 'type': 'rel', 'attr': 'href', 'base': 'https://www.empik.com'}
    }
```

EBOOK_DETAILS represent data saved in database. Put your queryselector and choose type:
```
# support option:
'text' -> get text from queryselector.
'decimal' -> get price as decimal from queryselector.
'attribute' -> get value from tag attribute.
'rel' -> join realitve links with 'base'
```
Create your __init__ only with future user input, next add your function for creating url.
```python
    def __init__(self, user_input):
        self.user_input = user_input
        self.bookstores_url = self.get_url()

    def get_url(self):
      #example
        if len(self.user_input.split()) < 2:
            return ''.join([self.BOOKSTORE_URL, self.user_input])
        return ''.join([self.BOOKSTORE_URL, '%20'.join(self.user_input.split())])
```

add your class to settings.py
```python
SCRAPER_BOOKSTORES = [
    # ...
    'NewBookstores',
    # ...
]
```
