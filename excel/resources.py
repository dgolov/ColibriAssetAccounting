from abc import abstractmethod
from datetime import date
from web.models import Asset, Location
from typing import Union

import logging


logger = logging.getLogger('main')


class AssetBase:
    @abstractmethod
    def set_price(self, price) -> None:
        pass

    @abstractmethod
    def set_status(self, status) -> None:
        pass

    @abstractmethod
    def set_state(self, state) -> None:
        pass

    @abstractmethod
    def set_year_of_purchase(self, year_of_purchase) -> None:
        pass


class AssetExcel(AssetBase):
    def __init__(
            self, name: str, location: Union[None, str] = None,
            price: Union[None, float] = None, year_of_purchase: Union[None, int] = None,
            status: Union[None, str] = None, state: Union[None, str] = None
    ):
        self.name = name
        self.location = location
        self.price = price
        self.status = status
        self.state = state
        self.year_of_purchase = year_of_purchase
        logger.info(f'[Excel.Asset] Created asset {self.name}')

    def __str__(self):
        return f"{self.name}"

    def set_attr(self, key: str, value: Union[str, float, int, None]) -> None:
        mapping_method = {
            "location": self.set_location,
            "price": self.set_price,
            "status": self.set_status,
            "state": self.set_state,
            "year_of_purchase": self.set_year_of_purchase
        }
        method = mapping_method.get(key, None)
        if method:
            method(value)

    def set_location(self, location) -> None:
        logger.debug(f'[Excel.Asset.set_location] Set location {location} for asset {self.name}')
        self.location = location

    def set_price(self, price) -> None:
        logger.debug(f'[Excel.Asset.set_price] Set price {price} for asset {self.name}')
        self.price = price

    def set_status(self, status) -> None:
        logger.debug(f'[Excel.Asset.set_status] Set status {status} for asset {self.name}')
        self.status = status

    def set_state(self, state) -> None:
        logger.debug(f'[Excel.Asset.set_state] Set state {state} for asset {self.name}')
        self.state = state

    def set_year_of_purchase(self, year_of_purchase) -> None:
        logger.debug(f'[Excel.Asset.set_year_of_purchase] Set year of purchase {year_of_purchase} for asset {self.name}')
        self.year_of_purchase = date(year=year_of_purchase, month=1, day=1)

    @staticmethod
    def map_status(value: str) -> str:
        status_mapping_dict = {
            "В работе": "in_work",
            "Сломано": "broken",
            "В ремонте": "under_repair",
            "В запасе": "in_reserve",
        }
        return status_mapping_dict.get(value, "")

    def save(self) -> Union[str, None]:
        logger.info(f"[Excel.Asset.save] Save asset '{self.name}' to database")
        try:
            location = Location.objects.get(name=self.location)
        except Location.DoesNotExist:
            logger.warning(
                f"[Excel.Asset.save] Save asset '{self.name}' warning. Location {self.location} is not found"
            )
            location = None
        status = self.map_status(self.status)
        if not status:
            logger.error(f"[Excel.Asset.save] Save asset '{self.name}' error - Status {self.status} is incorrect")
            message = f"Ошибка создания актива '{self.name}' - Неверно указан статус"
            return message
        try:
            Asset.objects.create(
                name=self.name,
                location=location,
                price=self.price,
                year_of_purchase=self.year_of_purchase,
                status=self.status,
                state=self.state
            )
        except Exception as e:
            logger.error(f"[Excel.Asset.save] Save asset '{self.name}' error - {e}")
            message = f"Ошибка создания актива '{self.name}' - {e}"
            return message
