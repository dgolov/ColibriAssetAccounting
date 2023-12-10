from django.test import TestCase, RequestFactory
from web.views import Search
from web.models import Asset, Location


class SearchViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_assets_and_locations(self):
        request = self.factory.get('/search/', {'search': 'some_query'})
        response = Search.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_ordering(self):
        request = self.factory.get('/search/', {'sort': 'name'})
        response = Search.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_ordering_desc(self):
        request = self.factory.get('/search/', {'sort': 'name', 'desc': 'true'})
        response = Search.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_empty_search_query(self):
        request = self.factory.get('/search/')
        response = Search.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Ничего не найдено...', response.content.decode("utf-8"))
