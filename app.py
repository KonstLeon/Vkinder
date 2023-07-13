import re
import threading

import requests
import vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import db
from vk_functions import search_users, get_photo, sort_likes, json_create, chat_keyboard
from db import engine, Session, register_user, add_to_favorites, add_to_checked_list, \
    check_db_user, get_favorites, take_position, delete_db_favorites, User, drop_db_checked_list, \
    update_position, search_user, drop_db_favorites, create_tables, update, take_db_user, take_last_partner_vk_id, get_checked_users
from vk_config import group_token, user_token, group_id

# Для работы с БД
session = Session()
connection = engine.connect()
# Для работы с вк_апи
vk_session = vk_api.VkApi(token=group_token)
vk= vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id)


class UserVK:
    def get_city(self, city):
        response = requests.get(
            'https://api.vk.com/method/database.getCities',
            Bot().get_params({'country_id': 1, 'count': 1, 'q': city})
        )
        try:
            response = response.json()['response']['items']
            if not response:
                Bot().write_msg(user_id, 'Город не найден')
                city = False
            else:
                for city_id in response:
                    city = city_id['id']
        except:
            print(f"Не удалось получить город пользователя для {user_id}: {response.json()['error']['error_msg']}")
            Bot().write_msg(user_id, 'Ошибка с нашей стороны. Попробуйте позже.')
            update(user_id, User, position=1, offset=0)
            city = False
        return city

    def get_age_range(self, message_text):
        age_range = re.findall(r'\d+', message_text)
        age_range = [int(i) for i in age_range]
        try:
            if len(age_range) == 1 and 18 <= age_range[0] <= 100:
                age_range.append(age_range[0])
                return age_range
            elif 18 <= age_range[0] < age_range[1] and age_range[0] < age_range[1] <= 100:
                return age_range
            else:
                Bot().write_msg(user_id, "Некорректный возраст")
        except:
            Bot().write_msg(user_id, "Некорректный возраст")

    def get_user_full_name(self, user_id):
        response = requests.get(
            'https://api.vk.com/method/users.get',
            Bot().get_params({'user_ids': user_id})
        )
        try:
            for user_info in response.json()['response']:
                first_name = user_info['first_name']
                last_name = user_info['last_name']
                return first_name + ' ' + last_name
        except:
            print(f"Не удалось получить имя пользователя для {user_id}: {response.json()['error']['error_msg']}")
            Bot().write_msg(user_id, 'Ошибка с нашей стороны. Попробуйте позже.')
            update(user_id, User, position=1, offset=0)
            return False


    def show_favorites(self, user_id):
        keyboard = chat_keyboard(['Продолжить поиск', 'Удалить', 'Меню'],
                                 [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE, VkKeyboardColor.PRIMARY])
        partners = get_favorites(user_id)
        message = f'Список избранных:\n'
        for partner in partners:
            message += f'https://vk.com/id{partner}\n'
        if len(partners) <= 0:
            message += "Список избранных пуст\n"
        Bot().write_msg(user_id, message, keyboard=keyboard.get_keyboard())


    def show_partner(self, id_user, partner_id, partner_full_name, link_profile):
        message = f"Фамилия и имя: {partner_full_name}\n" \
                  f"Ссылка: {link_profile}\n"
        photos = get_photo(partner_id)
        sorted_user_photo = sort_likes(photos)
        if len(sorted_user_photo) <= 0:
            message += photos

        keyboard = chat_keyboard(['Следующая анкета', 'Добавить в избранное', 'Список избранных'],
                                      [VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.PRIMARY])
        keyboard.add_line()
        keyboard.add_button('Меню', color=VkKeyboardColor.PRIMARY)
        Bot().write_msg(id_user, message, keyboard.get_keyboard())
        try:
            Bot().write_msg(id_user, f'Фото: ', keyboard.get_keyboard(),
                            attachment=','.join
                            ([sorted_user_photo[-1][1], sorted_user_photo[-2][1],
                              sorted_user_photo[-3][1]]))
        except IndexError:
            for photo in range(len(sorted_user_photo)):
                Bot().write_msg(id_user, f'Фото:', keyboard.get_keyboard(),
                                attachment=sorted_user_photo[photo][1])
        add_to_checked_list(take_db_user(user_id).id, partner_id)

    def search(self, id_user):
        user = take_db_user(id_user)
        city = user.city
        sex = user.target_gender
        age_from = user.age_from
        age_to = user.age_to
        offset = user.offset

        result = search_users(sex, age_from, age_to, 6, city, offset)

        if result == 'error':
            keyboard = chat_keyboard(['Поиск', 'Избранное', 'Сбросить анкету'],
                                     [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.SECONDARY])
            Bot().write_msg(user_id, "Произошла ошибка на нашей тороне. Попробуйте позже.", keyboard=keyboard.get_keyboard())
            update(user_id, User, position=5)
        elif result == 'not_find':
            keyboard = chat_keyboard(['Поиск', 'Избранное', 'Сбросить анкету'],
                                     [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.SECONDARY])
            Bot().write_msg(user_id, "Не удалось найти анкеты. Попробуйте снова.",
                            keyboard=keyboard.get_keyboard())
            update(user_id, User, position=5)
        # Производим отбор анкет
        for partner in result:
            checked_users = get_checked_users(user_id)
            if partner in checked_users:
                offset += 1
                update(user_id, User, offset=offset)
                self.search(user_id)
            else:
                offset += 1
                update(user_id, User, offset=offset)
                self.show_partner(user_id, partner[2], partner[0], partner[1])


class Bot:
    def get_params(self, add_params: dict = None):
        params = {
            'access_token': user_token,
            'v': '5.131'
        }
        if add_params:
            params.update(add_params)
            pass
        return params

    # Пишет сообщение пользователю
    def write_msg(self, user_id, message, keyboard='', attachment=''):
        try:
            vk_session.method('messages.send',
                      {'user_id': int(user_id),
                       'message': message,
                       'random_id': get_random_id(),
                       'attachment': attachment,
                       'keyboard':keyboard})
        except Exception as e:
            print(e)

    def processing_message(self, id_user, message_text):
        number_position = take_position(id_user)
        if number_position == 0:
            keyboard = chat_keyboard(['Старт'], [VkKeyboardColor.POSITIVE])
            self.write_msg(id_user, 'Вас приветствует бот - Vkinder. Заполните анкету.', keyboard.get_keyboard())
            reg_new_user(User(vk_id=user_id, position=1, offset=0))

        elif number_position == 1:
            if message_text == 'Старт':
                self.write_msg(user_id, "Введите ваш город")
                update(user_id, User, position=2, offset=0)

        #Ввод города
        elif number_position == 2:
            city = UserVK().get_city(message_text)
            if city:
                self.write_msg(user_id, "Введите диапозон возраста поиска в формате [от-до]")
                update(user_id, User, city=city, position=3)

        #Ввод дапозона возраста
        elif number_position == 3:
            target_age_range = UserVK().get_age_range(message_text)
            update(user_id, User, age_from=target_age_range[0], age_to=target_age_range[1])
            keyboard = chat_keyboard(['Мужской', 'Женский'], [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE])
            self.write_msg(user_id, "Ваш пол", keyboard=keyboard.get_keyboard())
            update(user_id, User, position=4)

        #Ввод пола
        elif number_position == 4:
            if message_text == 'Мужской' or message_text == 'Женский':
                if message_text == 'Мужской':
                    target_gender = 1
                else:
                    target_gender = 2
                user_info = UserVK().get_user_full_name(user_id)
                if user_info:
                    update(user_id, User, full_name=user_info, target_gender=target_gender, position=5)
                    keyboard = chat_keyboard(['Поиск', 'Избранное', 'Сбросить анкету'],
                                             [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.SECONDARY])
                    self.write_msg(user_id, "Анкета создана", keyboard=keyboard.get_keyboard())
                else:
                    return
            else:
                keyboard = chat_keyboard(['Мужской', 'Женский'], [VkKeyboardColor.POSITIVE, VkKeyboardColor.POSITIVE])
                self.write_msg(user_id, "Неизвестная комманда", keyboard=keyboard.get_keyboard())

        #Меню
        elif number_position == 5:
            if message_text == 'Поиск':
                keyboard = chat_keyboard(['Следующая анкета', 'Добавить в избранное', 'Список избранных'],
                                         [VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.PRIMARY])
                keyboard.add_line()
                keyboard.add_button('Меню', color=VkKeyboardColor.PRIMARY)
                update(user_id, User, position=6)
                self.write_msg(user_id, "Начинаем поиск.", keyboard.get_keyboard())
                UserVK().search(user_id)
            elif message_text == "Избранное":
                update(user_id, User, position=7)
                keyboard = chat_keyboard(['Продолжить поиск', 'Удалить', 'Меню'],
                                         [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE, VkKeyboardColor.PRIMARY])
                self.write_msg(user_id, "Переход в избранное.", keyboard.get_keyboard())
                UserVK().show_favorites(user_id)
            elif message_text == "Сбросить анкету":
                drop_db_favorites(user_id)
                drop_db_checked_list(user_id)
                self.write_msg(user_id, "Введите ваш город")
                update(user_id, User, position=2, offset=0)
            else:
                keyboard = chat_keyboard(['Поиск', 'Избранное', 'Сбросить анкету'],
                                         [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.SECONDARY])
                self.write_msg(user_id, "Неизвестная комманда", keyboard=keyboard.get_keyboard())

        #Поиск
        elif number_position == 6:
            if message_text == 'Следующая анкета':
                UserVK().search(user_id)
            elif message_text == 'Добавить в избранное':
                add_to_favorites(take_db_user(user_id).id, take_last_partner_vk_id().vk_id)
                self.write_msg(user_id, "Анкета добавлена в избранное")
                UserVK().search(user_id)
            elif message_text == 'Список избранных':
                UserVK().show_favorites(user_id)
                update(user_id, User, position=7)
            elif message_text == 'Меню':
                keyboard = chat_keyboard(['Поиск', 'Избранное', 'Сбросить анкету'],
                                         [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.SECONDARY])
                self.write_msg(user_id, "Переход в меню", keyboard=keyboard.get_keyboard())
                update(user_id, User, position=5)
            else:
                keyboard = chat_keyboard(['Следующая анкета', 'Добавить в избранное', 'Список избранных'],
                                         [VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.PRIMARY])
                keyboard.add_line()
                keyboard.add_button('Меню', color=VkKeyboardColor.PRIMARY)
                self.write_msg(user_id, "Неизвестная команда", keyboard=keyboard.get_keyboard())

        #Избранное
        elif number_position == 7:
            if message_text == 'Продолжить поиск':
                update(user_id, User, position=6)
                UserVK().search(user_id)
            elif message_text == 'Удалить':
                Bot().write_msg(user_id, "Введите vk_id человека из анкеты для удаления.")
                db.update(user_id, User, position=8)
            elif message_text == 'Меню':
                keyboard = chat_keyboard(['Поиск', 'Избранное', 'Сбросить анкету'],
                                         [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.SECONDARY])
                self.write_msg(user_id, "Переход в меню", keyboard=keyboard.get_keyboard())
                update(user_id, User, position=5)
            else:
                keyboard = chat_keyboard(['Продолжить поиск', 'Удалить', 'Меню'],
                                         [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE, VkKeyboardColor.PRIMARY])
                self.write_msg(user_id, "Неизвестная команда", keyboard.get_keyboard())
        elif number_position == 8:
            try:
                keyboard = chat_keyboard(['Продолжить поиск', 'Удалить', 'Меню'],
                                         [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE,
                                          VkKeyboardColor.PRIMARY])
                if int(message_text) in get_favorites(user_id):
                    delete_db_favorites(int(message_text))
                    db.delete_db_checked_list(int(message_text))
                    self.write_msg(user_id, "Анткета удалена из избранного", keyboard.get_keyboard())
                    UserVK().show_favorites(user_id)
                    update(user_id, User, position=7)
                else:
                    update(user_id, User, position=7)
                    self.write_msg(user_id, "Данного пользователя нет в избранном.", keyboard.get_keyboard())
            except Exception as e:
                print("Произошла ошибка при поиске списка избранных")
                keyboard = chat_keyboard(['Поиск', 'Избранное', 'Сбросить анкету'],
                                         [VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.SECONDARY])
                update(user_id, User, position=5)
                self.write_msg(user_id, "Ошибка с нашей стороны. Попробуйте позже.", keyboard.get_keyboard())


def reg_new_user(id_num):
    register_user(id_num)


if __name__ == '__main__':
    create_tables()
    try:
        while True:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                    user_id = event.object.message['from_id']
                    message = event.object.message['text']
                    thread = threading.Thread(target=Bot().processing_message, args=(user_id, message))
                    thread.start()
    except vk_api.exceptions.ApiError as error_msg:
        print(error_msg)

