from datetime import datetime
from django.test import TestCase
from web import models


class TestAsset(TestCase):
    """ Ткестирование модели активов
    """
    def setUp(self) -> None:
        models.Asset.objects.create(
            name="test",
            description="Test test",
            year_of_purchase=datetime(year=2023, month=1, day=1),
            price=300.5,
            state=3,
            status="in_work"
        )

    def test_asset_str(self):
        asset = models.Asset.objects.get(name="test")
        self.assertEqual(asset.__str__(), "test")
        self.assertEqual(asset.status, "in_work")
        self.assertEqual(asset.state, 3)

    def test_asset_description(self):
        asset = models.Asset.objects.get(name="test")
        self.assertEqual(asset.description, "Test test")


class TestLocation(TestCase):
    """ Ткестирование модели складов
    """
    def setUp(self) -> None:
        models.Location.objects.create(
            name="test",
            city="New York",
            address="Test test",
            description="Test description"
        )

    def test_location_str(self):
        location = models.Location.objects.get(name="test")
        self.assertEqual(location.__str__(), "test")
        self.assertEqual(location.city, "New York")
        self.assertEqual(location.address, "Test test")

    def test_location_description(self):
        location = models.Location.objects.get(name="test")
        self.assertEqual(location.description, "Test description")

    def test_update_location(self):
        location = models.Location.objects.get(name="test")
        location.address = "Test"
        location.save()
        self.assertEqual(location.address, "Test")
