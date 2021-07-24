import requests
from pprint import pprint
import json
# Токен VK(сервисный)
token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
# Токен Яндекс.Диска
with open('yandex_token.txt') as file:
    token_ya = file.read()


def _get_upload_link(disk_file_path):
    '''Служебная функция для получения ссылки для загрузки в Яндекс.Диск'''
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {'Authorization': token_ya}
    params = {"path": disk_file_path, "overwrite": True}
    response = requests.get(upload_url, headers=headers, params=params)
    return response.json()


def upload_file_to_disk(disk_file_path, filename):
    '''Функция для загрузки файла в Яндекс.Диск'''
    href = _get_upload_link(disk_file_path=disk_file_path).get("href", "")
    response = requests.put(href, data=open(filename, 'rb'))
    response.raise_for_status()


def get_user_info(user_ids):
    '''Функция для получения информации о пользователе по имени его страницы'''
    url = f"https://api.vk.com/method/users.get"
    params = {'user_ids': user_ids, 'access_token': token, 'v': '5.131'}
    response = requests.get(url, params=params)
    resp = response.json()
    print(resp)


def _get_biggest_photo(photo_list):
    '''Принимает на вход список фотографий разного размера и возвращает индекс фотографии максимального рамера'''
    b_size = 0
    index = 0
    for element in photo_list:
        size = element.get('height') * element.get('width')
        if size > b_size:
            b_size = size
            index = photo_list.index(element)
        else:
            pass
    return index


def get_photos(user_id):
    '''Функция скачивания фотографий со страницы указанного пользователя и загрузки в Яндекс.Диск'''
    url = f"https://api.vk.com/method/photos.get"
    params = {'owner_id': user_id, 'album_id': 'profile', 'access_token': token, 'v': '5.131', 'extended': '1'}
    response = requests.get(url, params=params)
    resp = response.json()
    print(f"Найдено {len(resp.get('response').get('items'))} фотографий.")
    fname_list = []
    data = []
    i = 0
    # Блок загрузки фото из VK, с кол-вом лайков в качестве имени файла.
    # Если у нескольких фото одинаковое кол-во лайков, к имени добавляется ID фотографии.
    for item in resp.get('response').get('items'):
        i += 1
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
    with open("data_file.json", "w") as write_file:
        json.dump(data, write_file)
    # Блок загрузки фотографий на Яндекс.Диск
    u = 0
    for item in fname_list:
        u += 1
        upload_file_to_disk(disk_file_path=f"netology_hw/vk_api/{item}/", filename=f"{item}.jpg")
        print(f"Файл {item} загружен на Яндекс.Диск ({round((u/len(fname_list))*100, 2)}%)")


# get_user_info('begemot_korovin')
get_photos('552934290')