import requests
import vk_api
import json
import datetime

from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_config import group_token, user_token, V
from vk_api.exceptions import ApiError
from db import engine, Base, Session, User, DatingUser, CheckedList, update
from sqlalchemy.exc import IntegrityError, InvalidRequestError

# Для работы с ВК
vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)
# Для работы с БД
session = Session()
connection = engine.connect()


def create_buttons(names: list, colors: list, keyboard):
    return chat_keyboard(buttons=names, button_colors=colors)


def chat_keyboard(buttons, button_colors):
    keyboard = VkKeyboard.get_empty_keyboard()
    keyboard = VkKeyboard(one_time=True)
    for btn, btn_color in zip(buttons, button_colors):
        keyboard.add_button(btn, btn_color)
    return keyboard


""" 
ФУНКЦИИ ПОИСКА
"""

# Ищет людей по критериям
def search_users(sex, age_from, age_to, status, city, offset):
    all_persons = []
    link_profile = 'https://vk.com/id'
    vk_ = vk_api.VkApi(token=user_token)
    try:
        response = vk_.method('users.search',
                          {'sex': sex,
                           'offset': offset,
                           'city': city,
                           'status': status,
                           'age_from': age_from,
                           'age_to': age_to,
                           'has_photo': 1,
                           'count': 1
                           })
    except Exception as error_msg:
        print(error_msg)
        return 'error'

    if 'items' not in response.keys():
        print('В ответе нет ключа "items"')
        return 'not_find'

    for element in response['items']:
        person = [
            element['first_name'] + ' ' + element['last_name'],
            link_profile + str(element['id']),
            element['id']
        ]
        all_persons.append(person)
    return all_persons
    # return True


# Находит фото людей
def get_photo(user_owner_id):
    vk_ = vk_api.VkApi(token=user_token)
    try:
        response = vk_.method('photos.get',
                              {
                                  'access_token': user_token,
                                  'v': V,
                                  'owner_id': user_owner_id,
                                  'album_id': 'profile',
                                  'count': 10,
                                  'extended': 1,
                                  'photo_sizes': 1,
                              })
    except ApiError:
        return 'нет доступа к фото'
    users_photos = []
    for i in range(10):
        try:
            users_photos.append(
                [response['items'][i]['likes']['count'],
                 'photo' + str(response['items'][i]['owner_id']) + '_' + str(response['items'][i]['id'])])
        except IndexError:
            users_photos.append(['нет фото.'])
    return users_photos
    # return True


""" 
ФУНКЦИИ СОРТИРОВКИ, ОТВЕТА, JSON
"""


# Сортируем фото по лайкам, удаляем лишние элементы
def sort_likes(photos):
    result = []
    for element in photos:
        if element != ['нет фото.'] and photos != 'нет доступа к фото':
            result.append(element)
    return sorted(result)


# JSON file create with result of programm
def json_create(lst):
    today = datetime.date.today()
    today_str = f'{today.day}.{today.month}.{today.year}'
    res = {}
    res_list = []
    for num, info in enumerate(lst):
        res['data'] = today_str
        res['first_name'] = info[0]
        res['second_name'] = info[1]
        res['link'] = info[2]
        res['id'] = info[3]
        res_list.append(res.copy())

    with open("result.json", "a", encoding='UTF-8') as write_file:
        json.dump(res_list, write_file, ensure_ascii=False)

    print(f'Информация о загруженных файлах успешно записана в json файл.')
