from typing import List

import requests

from robotoff.utils import get_logger

http_session = requests.Session()

POST_URL = "https://world.openfoodfacts.org/cgi/product_jqm2.pl"
AUTH = ("roboto-app", "4mbN9wJp8LBShcH")
AUTH_DICT = {
    'user_id': AUTH[0],
    'password': AUTH[1],
}

API_URL = "https://world.openfoodfacts.org/api/v0"
PRODUCT_URL = API_URL + "/product"

logger = get_logger(__name__)


def get_product(product_id: str, fields: List[str]=None):
    fields = fields or []
    url = PRODUCT_URL + "/{}.json".format(product_id)

    if fields:
        # requests escape comma in URLs, as expected, but openfoodfacts server
        # does not recognize escaped commas.
        # See https://github.com/openfoodfacts/openfoodfacts-server/issues/1607
        url += '?fields={}'.format(','.join(fields))

    r = http_session.get(url)

    if r.status_code != 200:
        return

    data = r.json()

    if data['status_verbose'] != 'product found':
        return

    return data['product']


def save_category(product_id: str, category: str):
    params = {
        'code': product_id,
        'add_categories': category,
        **AUTH_DICT
    }

    r = http_session.get(POST_URL, params=params)
    r.raise_for_status()
    json = r.json()

    status = json.get('status_verbose')

    if status != "fields saved":
        logger.warn("Unexpected status during category update: {}".format(status))


def save_ingredients(barcode: str, ingredient_text: str, lang: str=None):
    ingredient_key = 'ingredients_text' if lang is None else f'ingredients_{lang}_text'
    params = {
        'code': barcode,
        ingredient_key: ingredient_text,
        **AUTH_DICT,
    }

    r = http_session.get(POST_URL, params=params)
    r.raise_for_status()
    json = r.json()

    status = json.get('status_verbose')

    if status != "fields saved":
        logger.warn("Unexpected status during update: {}".format(status))


def add_emb_code(barcode: str, emb_code: str):
        params = {
            'code': barcode,
            'add_emb_codes': emb_code,
            **AUTH_DICT,
        }

        r = http_session.get(POST_URL, params=params)
        r.raise_for_status()
        json = r.json()

        status = json.get('status_verbose')

        if status != "fields saved":
            logger.warn(
                "Unexpected status during product update: {}".format(
                    status))
