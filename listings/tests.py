import csv
import sys

import pytest
from django.urls import reverse

from listings.models import Listing, HotelRoomType, HotelRoom, BookingInfo, Blocked

pytestmark = pytest.mark.django_db
listing_list_url = reverse('listing-list')

@pytest.fixture
def import_data():
    tables = {'Listing', 'HotelRoomType', 'HotelRoom', 'BookingInfo', 'Blocked', }
    for table in tables:
        with open(f'./listings/{table}.csv','r') as f:
            reader = csv.reader(f, delimiter='\t')
            headers = next(reader)

            table_object = getattr(sys.modules[__name__], table)
            for row in reader:
                row = [None if f == '(null)' else f for f in row]
                data = dict(zip(headers, row))
                table_object.objects.create(**data)


def test_get_units_max_price_50_blocked_dates(client, import_data) -> None:
    """
    Check if url returns the correct records imported based on search criteria
    """
    response = client.get(listing_list_url, {'max_price': 50, 'check_in': '2022-01-11', 'check_out': '2022-01-12'})
    assert response.status_code == 200
    result = response.data
    assert len(result) == 1
    assert result[0]['id'] == 1


def test_get_units_max_price_60_blocked_dates(client, import_data) -> None:
    """
    Check if url returns the correct records imported based on search criteria
    """
    response = client.get(listing_list_url, {'max_price': 60, 'check_in': '2022-01-11', 'check_out': '2022-01-12'})
    assert response.status_code == 200
    result = response.data
    assert len(result) == 1
    assert result[0]['id'] == 1


def test_get_units_max_price_70_blocked_dates(client, import_data) -> None:
    """
    Check if url returns the correct records imported based on search criteria
    """
    response = client.get(listing_list_url, {'max_price': 70, 'check_in': '2022-01-11', 'check_out': '2022-01-12'})
    assert response.status_code == 200
    result = response.data
    assert len(result) == 2
    assert result[0]['id'] == 1
    assert result[1]['id'] == 4


def test_get_units_max_price_200(client, import_data) -> None:
    """
    Check if url returns the correct records imported based on search criteria
    """
    response = client.get(listing_list_url, {'max_price': 200})
    assert response.status_code == 200
    result = response.data
    assert len(result) == 5
