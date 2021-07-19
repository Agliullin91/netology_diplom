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
    pprint(response.json())
    return response.json()


def upload_file_to_disk(disk_file_path, filename):
    '''Функция для загрузки файла в Яндекс.Диск'''
    href = _get_upload_link(disk_file_path=disk_file_path).get("href", "")
    response = requests.put(href, data=open(filename, 'rb'))
    response.raise_for_status()
    if response.status_code == 201:
        print("Success")


def get_user_info(user_ids):
    '''Функция для получения информации о пользователе по имени его страницы'''
    url = f"https://api.vk.com/method/users.get"
    params = {'user_ids': user_ids, 'access_token': token, 'v': '5.131'}
    response = requests.get(url, params=params)
    resp = response.json()
    print(resp)


def get_photos(user_id):
    '''Функция скачивания фотографий со страницы указанного пользователя и загрузки в Яндекс.Диск'''
    url = f"https://api.vk.com/method/photos.get"
    params = {'owner_id': user_id, 'album_id': 'profile', 'access_token': token, 'v': '5.131', 'extended': '1'}
    response = requests.get(url, params=params)
    resp = response.json()
    pprint(resp.get('response').get('items'))
    fname_list = []
    data = []
    # Блок загрузки фото из VK, с кол-вом лайков в качестве имени файла.
    # Если у нескольких фото одинаковое кол-во лайков, к имени добавляется ID фотографии.
    for item in resp.get('response').get('items'):
        if item.get('likes').get('count') not in fname_list:
            fname = item.get('likes').get('count')
            fname_list.append(fname)
            data.append({"file_name": f'{fname}.jpg', 'size': item.get('sizes')[-1].get('type')})
            r = requests.get(item.get('sizes')[-1].get('url'))
            with open(fr'C:\netology_vk_api\{fname}.jpg', 'wb') as f:
                f.write(r.content)
        else:
            fname = f"{item.get('likes').get('count')}_{item.get('id')}"
            fname_list.append(fname)
            data.append({"file_name": f'{fname}.jpg', 'size': item.get('sizes')[-1].get('type')})
            r = requests.get(item.get('sizes')[-1].get('url'))
            with open(fr'C:\netology_vk_api\{fname}.jpg', 'wb') as f:
                f.write(r.content)
    # Блок записи информации в json-файл.
    with open("data_file.json", "w") as write_file:
        json.dump(data, write_file)
    # Блок загрузки фотографий на Яндекс.Диск
    for item in fname_list:
        upload_file_to_disk(disk_file_path=f"netology_hw/vk_api/{item}/", filename=f"{item}.jpg")


get_user_info('begemot_korovin')
get_photos('552934290')