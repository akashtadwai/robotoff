import re
from typing import Set

import pytest

from robotoff import settings
from robotoff.insights.ocr.brand import (
    generate_brand_keyword_processor,
    extract_brands_taxonomy,
)
from robotoff.taxonomy import Taxonomy
from robotoff.utils import text_file_iter


def test_check_logo_annotation_brands():
    items: Set[str] = set()

    for item in text_file_iter(settings.OCR_LOGO_ANNOTATION_BRANDS_DATA_PATH):
        assert "||" in item
        assert item not in items
        items.add(item)


@pytest.fixture(scope="session")
def brand_keyword_processor():
    yield generate_brand_keyword_processor(min_length=6)


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "Le comptoir de Mathilde bon vous propose",
            {
                "brand": "Le Comptoir de Mathilde",
                "brand_tag": "le-comptoir-de-mathilde",
                "text": "Le comptoir de Mathilde",
                "data-source": "test",
            },
        ),
        ("Netto gewitch: 450 g", None),
        ("", None),
        (
            "Notre marque Alpina savoie est bien positionnée",
            {
                "brand": "Alpina Savoie",
                "brand_tag": "alpina-savoie",
                "text": "Alpina savoie",
                "data-source": "test",
            },
        ),
    ],
)
def test_extract_brand_taxonomy(brand_keyword_processor, text: str, expected):
    insights = extract_brands_taxonomy(brand_keyword_processor, text, "test")

    if not expected:
        assert not insights
    else:
        insight = insights[0]
        for expected_key, expected_value in expected.items():
            assert expected_key in insight
            assert insight[expected_key] == expected_value
