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


def upload_file_to_disk(disk_file_path, filename):
    """Функция для загрузки файла в Яндекс.Диск"""
    href = _get_upload_link(disk_file_path=disk_file_path).get("href", "")
    response = requests.put(href, data=open(filename, 'rb'))
    response.raise_for_status()


def get_user_info(user_ids):
    '''Функция для получения информации о пользователе по имени его страницы'''
    resp = _resp_check('users.get', params = {'user_ids': user_ids, 'access_token': token_vk, 'v': '5.131'})
    return resp


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
    else:
        resp = response.json()
        if 'error' in resp:
            print(f"Server responded with error: {resp.get('error')}")
        else:
            return resp


def _cr_json_datafile(data):
    """Служебная. Записывает сформированные данные в JSON файл"""
    with open("data_file.json", "w") as write_file:
        json.dump(data, write_file)
    print(f'JSON file created. {write_file}')


def _upload_yadisc(fname_list):
    """Служебная. Загружает фото на Я.диск"""
    for u, item in enumerate(fname_list, start=1):
        upload_file_to_disk(disk_file_path=f"netology_hw/vk_api/{item}/", filename=f"{item}.jpg")
        print(f"Файл {item} загружен на Яндекс.Диск ({round((u/len(fname_list))*100, 2)}%)")


def get_photos(user_id):
    '''Основная функция. Скачивает фотографий со страницы указанного пользователя и загружает на Яндекс.Диск'''
    resp = _resp_check('photos.get', params = {'owner_id': user_id, 'album_id': 'profile', 'access_token': token_vk, 'v': '5.131', 'extended': '1'})
    fname_list = []
    data = []
    # Блок загрузки фото из VK, с кол-вом лайков в качестве имени файла.
    # Если у нескольких фото одинаковое кол-во лайков, к имени добавляется ID фотографии.
    for i, item in enumerate(resp.get('response').get('items'), start=1):
        if item.get('likes').get('count') not in fname_list:
            fname = item.get('likes').get('count')
            fname_list.append(fname)
            data.append({"file_name": f'{fname}.jpg', 'size': item.get('sizes')[_get_biggest_photo(item.get('sizes'))].get('type')})
            r = requests.get(item.get('sizes')[_get_biggest_photo(item.get('sizes'))].get('url'))
            with open(fr'C:\netology_vk_api\{fname}.jpg', 'wb') as f:
                f.write(r.content)
            print(f"{fname}.jpg: фото загружено на жесткий диск ({round((i/len(resp.get('response').get('items')))*100, 2)}%)")
        else:
            fname = f"{item.get('likes').get('count')}_{item.get('id')}"
            fname_list.append(fname)
            data.append({"file_name": f'{fname}.jpg', 'size': item.get('sizes')[_get_biggest_photo(item.get('sizes'))].get('type')})
            r = requests.get(item.get('sizes')[_get_biggest_photo(item.get('sizes'))].get('url'))
            with open(fr'C:\netology_vk_api\{fname}.jpg', 'wb') as f:
                f.write(r.content)
            print(f"{fname}.jpg: фото загружено на жесткий диск ({round((i/len(resp.get('response').get('items')))*100, 2)}%)")
    # Блок записи информации в json-файл.
    _cr_json_datafile(data)
    # Блок загрузки фотографий на Яндекс.Диск
    _upload_yadisc(fname_list)


if __name__ == "__main__":
    get_photos('552934290')