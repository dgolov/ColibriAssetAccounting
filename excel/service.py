import logging
import os
import pandas as pd

from datetime import datetime
from django.conf import settings
from excel.resources import AssetExcel


logger = logging.getLogger('main')


def parse_import(file_name: str) -> dict:
    """ Парсинг файла excel импорта активов
    :param file_name: путь к файлу
    :return:
    """
    logger.info("[Parse excel] Start parsing data")
    df = pd.read_excel(file_name)
    successfully_upload_count = 0
    failed_upload_count = 0
    messages = {
        "success": [],
        "error": [],
    }

    columns_list = df.columns.tolist()
    if any(columns_list[i] != settings.ASSET_UPLOAD_FORMAT[i] for i, _ in enumerate(settings.ASSET_UPLOAD_FORMAT)):
        logger.error("[Parse excel] Incorrect excel data")
        messages.get("Error").append("Ошибка парсинга файла. Неверный формат столбцов.")
        os.remove(file_name)
        return messages

    for columns_index, name in enumerate(df[columns_list[0]].tolist()):
        asset = AssetExcel(name=name)
        for fields_index, column_name in enumerate(columns_list[1:], start=1):
            field = settings.ASSET_UPLOAD_FIELDS[fields_index]
            asset.set_attr(key=field, value=df[column_name].tolist()[columns_index])
        error = asset.save()
        if not error:
            successfully_upload_count += 1
        else:
            failed_upload_count += 1
            messages.get("error").append(error)

    messages.get("success").append(f"Успешно загружено {successfully_upload_count} активов")
    if failed_upload_count:
        messages.get("error").append(f"Не было загружено {failed_upload_count} активов")
    os.remove(file_name)

    return messages


def handle_uploaded_file(file) -> str:
    """ Загрузка файла
    :param file: Файл импорта активов
    :return: путь загруженного файла
    """
    path = "media/uploads/"
    check_path(path=path)

    path += f"{file}"

    with open(path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return f"{path}"


def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_order(order_id, asset_list: list):
    """ Создание файла отчета
    :param order_id: id отчета
    :param asset_list: список активов
    :return: путь к файлу отчета
    """
    data = {
        'Наименование': [],
        'Местоположение': [],
        'Стоимость': [],
        'Год закупкки': [],
        'Статус': [],
        'Состояние': [],
    }

    for asset in asset_list:
        location_name = None if not asset.location else asset.location.name
        data.get('Наименование').append(asset.name)
        data.get('Местоположение').append(location_name)
        data.get('Стоимость').append(asset.price)
        data.get('Год закупкки').append(asset.year_of_purchase.year)
        data.get('Статус').append(asset.status)
        data.get('Состояние').append(asset.state)
    df = pd.DataFrame(data)

    path = "media/orders/"
    check_path(path=path)
    name = datetime.now().strftime("%Y-%m-%d") + f"_{order_id}"
    path += f'{name}.xlsx'
    df.to_excel(path)

    return path
