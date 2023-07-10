from datetime import datetime
from django.test import TestCase
from web import models


class TestAsset(TestCase):
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
