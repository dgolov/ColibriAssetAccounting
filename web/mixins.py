from django.contrib.auth.mixins import LoginRequiredMixin
from typing import Union
from web.models import Asset, History, Location
from web.services import connect_to_redis

import logging


logger = logging.getLogger('main')


class UserMixin(LoginRequiredMixin):
    """ Миксин пользователей
    """
    login_url = '/auth'


class AssetMixin:
    """ Миксин функций активов
    """
    try:
        r = connect_to_redis()
    except Exception as e:
        logger.error(f"[AssetMixin] Connect to redis error - {e}")
        r = None

    def save_old_asset_data(self, asset: Asset):
        """ Сохраняет данные в редис
        """
        if not self.r:
            return

        self.r.set(f'{asset.pk}_name', asset.name, 120)
        self.r.set(f'{asset.pk}_location', asset.location.pk, 120)
        self.r.set(f'{asset.pk}_price', f"{asset.price}", 120)
        self.r.set(f'{asset.pk}_state', f"{asset.state}", 120)
        self.r.set(f'{asset.pk}_status', f"{asset.status}", 120)

        logger.info(f"[AssetMixin] Save redis data for asset if {asset.pk}")

    def get_old_asset_data(self, asset_id: int) -> Union[dict, None]:
        """ Забирает данные из редиса
        """
        if not self.r:
            return None
        location_id = self.r.get(f'{asset_id}_location')
        location = Location.objects.get(pk=location_id)

        logger.info(f"[AssetMixin] Get redis data for asset if {asset_id}")

        return {
            "name": self.r.get(f'{asset_id}_name').decode(),
            "location": location,
            "price": float(self.r.get(f'{asset_id}_price')),
            "state": int(self.r.get(f'{asset_id}_state')),
            "status": self.r.get(f'{asset_id}_status').decode()
        }

    def create_asset_history(self, new_asset: Asset):
        """ При изменении актива создает запись в историю на основе данных записаных в редис (о старом активе)
        """
        old_asset = self.get_old_asset_data(asset_id=new_asset.pk)
        if not old_asset:
            return None

        if new_asset.name != old_asset.get('name'):
            logger.debug(f"[AssetMixin] Create asset history for name field asset id - {new_asset.pk}")
            History.objects.create(
                asset=new_asset,
                old_name=old_asset.get('name'),
                new_name=new_asset.name,
                event_name="Изменение названия"
            )

        if new_asset.location != old_asset.get('location'):
            logger.debug(f"[AssetMixin] Create asset history for location field asset id - {new_asset.pk}")
            History.objects.create(
                asset=new_asset,
                old_location=old_asset.get('location'),
                new_location=new_asset.location,
                event_name="Изменение склада"
            )

        if new_asset.price != old_asset.get('price'):
            logger.debug(f"[AssetMixin] Create asset history for price field asset if - {new_asset.pk}")
            History.objects.create(
                asset=new_asset,
                old_price=old_asset.get('price'),
                new_price=new_asset.price,
                event_name="Изменение цены"
            )

        if new_asset.state != old_asset.get('state'):
            logger.debug(f"[AssetMixin] Create asset history for state field asset if - {new_asset.pk}")
            History.objects.create(
                asset=new_asset,
                old_state=old_asset.get('state'),
                new_state=new_asset.state,
                event_name="Изменение состояния"
            )

        if new_asset.status != old_asset.get('status'):
            logger.debug(f"[AssetMixin] Create asset history for status field asset if - {new_asset.pk}")
            History.objects.create(
                asset=new_asset,
                old_status=old_asset.get('status'),
                new_status=new_asset.status,
                event_name="Изменение статуса"
            )

