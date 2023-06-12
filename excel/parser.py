import logging
import pandas as pd

from django.conf import settings
from excel.resources import AssetExcel


logger = logging.getLogger('main')


def parse_import(file_name):
    logger.info("[Parse excel] Start parsing data")
    df = pd.read_excel(file_name)

    columns_list = df.columns.tolist()
    if any(columns_list[i] != settings.ASSET_UPLOAD_FORMAT[i] for i, _ in enumerate(settings.ASSET_UPLOAD_FORMAT)):
        logger.error("[Parse excel] Incorrect excel data")
        return

    for columns_index, name in enumerate(df[columns_list[0]].tolist()):
        asset = AssetExcel(name=name)
        for fields_index, column_name in enumerate(columns_list[1:], start=1):
            field = settings.ASSET_UPLOAD_FIELDS[fields_index]
            asset.set_attr(key=field, value=df[column_name].tolist()[columns_index])
        asset.save()
