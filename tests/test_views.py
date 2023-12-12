from django.test import TestCase, RequestFactory
from web import views, models


class MainViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class AuthViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class LogOutViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class ProfileViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class SearchViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_assets_and_locations(self):
        request = self.factory.get('/search/', {'search': 'some_query'})
        response = views.Search.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_ordering(self):
        request = self.factory.get('/search/', {'sort': 'name'})
        response = views.Search.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_ordering_desc(self):
        request = self.factory.get('/search/', {'sort': 'name', 'desc': 'true'})
        response = views.Search.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_empty_search_query(self):
        request = self.factory.get('/search/')
        response = views.Search.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Ничего не найдено...', response.content.decode("utf-8"))


class AssetListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class AssetDetailViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class CreateAssertViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class CreateAssertImageViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class DeleteAssertImageViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class UpdateAssetViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class CloneAssertViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class DeleteAssertViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class LocationListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class LocationDetailViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class CreateLocationViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class UpdateLocationViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class DeleteLocationViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class OrderListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class CreateOrderViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class AssetsImportViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


class NotificationsListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_queryset(self):
        user = models.CustomUser.objects.create(username='testuser')
        request = self.factory.get('/notifications/')
        request.user = user
        response = views.NotificationsListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('notifications' in response.context_data)
        notifications = response.context_data['notifications']
        self.assertEqual(notifications.count(), views.Notifications.objects.filter(user=user).count())

    def test_context_data(self):
        user = models.CustomUser.objects.create(username='testuser')
        request = self.factory.get('/notifications/')
        request.user = user
        response = views.NotificationsListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('title' in response.context_data)
        title = response.context_data['title']
        self.assertEqual(title, 'Уведомления')

    # def test_pagination(self):
    #     user = User.objects.create(username='testuser')
    #     notifications = NotificationsFactory.create_batch(35, user=user)
    #     request = self.factory.get('/notifications/')
    #     request.user = user
    #     response = views.NotificationsListView.as_view()(request)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue('notifications' in response.context_data)
    #     notifications = response.context_data['notifications']
    #     self.assertEqual(len(notifications), 30)
