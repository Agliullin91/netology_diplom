import requests
from pprint import pprint
import json
from config import token_vk, token_ya


def _get_upload_link(disk_file_path):
    """Служебная функция для получения ссылки для загрузки в Яндекс.Диск"""
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {'Authorization': token_ya}
    params = {"path": disk_file_path, "overwrite": True}
    response = requests.get(upload_url, headers=headers, params=params)
    return response.json()


def _upload_file_to_disk(disk_file_path, filename):
    """Служебная. Функция для загрузки файла в Яндекс.Диск"""
    href = _get_upload_link(disk_file_path=disk_file_path).get("href", "")
    response = requests.put(href, data=open(filename, 'rb'))
    response.raise_for_status()


def _get_user_id(user_pagename):
    '''Служебная. Функция для получения ID пользователя по имени его страницы'''
    resp = _resp_check('users.get', params = {'user_ids': user_pagename, 'access_token': token_vk, 'v': '5.131'})
    return resp.get('response')[0].get('id')


def _get_biggest_photo(photo_list):
    """Служебная. Принимает на вход список фотографий разного размера и возвращает индекс фотографии макс. рамера"""
    b_size = 0
    index = 0
    for element in photo_list:
        size = element.get('height') * element.get('width')
        if size > b_size:
            b_size = size
            index = photo_list.index(element)
    return index


def _resp_check(method_name, params):
    """Служебная. Функция обработки ошибок"""
    url = f"https://api.vk.com/method/{method_name}"
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return f'Request error: {response.status_code}'
    resp = response.json()
    if 'error' in resp:
        print(f"Server responded with error: {resp.get('error')}")
    else:
        return resp


def _download(fname, url, i, items):
    """Служебная. Функция для скачивания фото на жесткий диск пользователя"""
    with open(fr'C:\netology_vk_api\{fname}.jpg', 'wb') as f:
        f.write(url.content)
    print(f"{fname}.jpg: фото загружено на жесткий диск ({round((i / len(items)) * 100, 2)}%)")


def _cr_json_datafile(data):
    """Служебная. Записывает сформированные данные в JSON файл"""
    with open("data_file.json", "w") as write_file:
        json.dump(data, write_file)
    print(f'JSON file created. {write_file}')


def _upload_yadisc(fname_list):
    """Служебная. Загружает фото на Я.диск"""
    for u, item in enumerate(fname_list, start=1):
        _upload_file_to_disk(disk_file_path=f"netology_hw/vk_api/{item}/", filename=f"{item}.jpg")
        print(f"Файл {item} загружен на Яндекс.Диск ({round((u/len(fname_list))*100, 2)}%)")


def get_photos(user_pagename):
    '''Основная функция. Скачивает фотографий со страницы указанного пользователя и загружает на Яндекс.Диск'''
    user_id = _get_user_id(user_pagename)
    resp = _resp_check('photos.get', params = {'owner_id': user_id, 'album_id': 'profile', 'access_token': token_vk, 'v': '5.131', 'extended': '1'})
    fname_list = []
    data = []
    # Блок загрузки фото из VK, с кол-вом лайков в качестве имени файла.
    # Если у нескольких фото одинаковое кол-во лайков, к имени добавляется ID фотографии.
    items = resp.get('response').get('items')
    for i, item in enumerate(items, start=1):
        if item.get('likes').get('count') not in fname_list:
            fname = item.get('likes').get('count')
        else:
            fname = f"{item.get('likes').get('count')}_{item.get('id')}"
        fname_list.append(fname)
        bp_index = _get_biggest_photo(item.get('sizes'))
        data.append({"file_name": f'{fname}.jpg', 'size': item.get('sizes')[bp_index].get('type')})
        url = requests.get(item.get('sizes')[bp_index].get('url'))
        _download(fname, url, i, items)
    # Блок записи информации в json-файл.
    _cr_json_datafile(data)
    # Блок загрузки фотографий на Яндекс.Диск
    _upload_yadisc(fname_list)


if __name__ == "__main__":
    get_photos('begemot_korovin')