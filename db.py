import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType

import db
from vk_config import group_token
from random import randrange
from vk_api import VkUpload

import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError


# Подключение к БД
Base = declarative_base()
engine = sq.create_engine('postgresql://postgres:ngqarstwxwz@localhost:5432/vkpoint',
                          client_encoding='utf8')
Session = sessionmaker(bind=engine)
# Для работы с ВК
vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)
# Для работы с БД
session = Session()
connection = engine.connect()

# Пользователь бота ВК
class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    full_name = sq.Column(sq.String)
    age_from = sq.Column(sq.Integer)
    age_to = sq.Column(sq.Integer)
    target_gender = sq.Column(sq.Integer)
    city = sq.Column(sq.String)
    position=sq.Column(sq.Integer)
    offset = sq.Column(sq.Integer)

# Анкеты добавленные в избранное
class DatingUser(Base):
    __tablename__ = 'dating_user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))

# Просмотренные анкеты
class CheckedList(Base):
    __tablename__ = 'checked_list'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))

""" 
ФУНКЦИИ РАБОТЫ С БД
"""

# Удаляет пользователя из черного списка
def delete_db_checked_list(ids):
    current_user = session.query(CheckedList).filter_by(vk_id=ids).first()
    session.delete(current_user)
    session.commit()


def delete_db_favorites(ids):
    current_user = session.query(DatingUser).filter_by(vk_id=ids).first()
    session.delete(current_user)
    session.commit()

# Удаляет пользователя из избранного
def drop_db_favorites(ids):
    db_user = take_db_user(ids).id
    favorites = session.query(DatingUser).filter_by(id_user=db_user).all()
    for favirite in favorites:
        session.delete(favirite)
        session.commit()

def drop_db_checked_list(user_id):
    db_user = take_db_user(user_id).id
    checked_list = session.query(CheckedList).filter_by(id_user=db_user).all()
    for checked in checked_list:
        session.delete(checked)
        session.commit()

# проверят есть ли юзер в бд
def check_db_user(ids):
    dating_user = session.query(DatingUser).filter_by(
        vk_id=ids).first()
    blocked_user = session.query(CheckedList).filter_by(
        vk_id=ids).first()
    return dating_user, blocked_user


# Проверят есть ли юзер в черном списке
def get_checked_users(ids):
    current_users_id = session.query(User).filter_by(vk_id=ids).first()
    # Находим все анкеты из избранного которые добавил данный юзер
    all_users = session.query(CheckedList).filter_by(id_user=current_users_id.id).all()
    return all_users


# Проверяет есть ли юзер в избранном
def get_favorites(ids):
    current_users_id = session.query(User).filter_by(vk_id=ids).first()
    # Находим все анкеты из избранного которые добавил данный юзер
    alls_users = session.query(DatingUser).filter_by(id_user=current_users_id.id).all()

    favorites_ids = []
    for user in alls_users:
        favorites_ids.append(user.vk_id)

    return favorites_ids



# Регистрация пользователя
def register_user(user):
    try:

        if session.query(User.vk_id).filter(User.vk_id == user.vk_id).first() is not None:
            return False
        else:
            session.add(user)
            session.commit()
        return True
    except (IntegrityError, InvalidRequestError):
        return False

def  update_position(id_user, position):
    try:
        user=session.query(User).filter_by(vk_id=id_user).first()
        user.position = position
        session.commit()
    finally:
        print('Позиция обновлена')

# Сохранение выбранного пользователя в БД
def add_to_favorites(id_user, vk_id):
    try:
        new_user = DatingUser(
            vk_id=vk_id,
            id_user=id_user
        )
        session.add(new_user)
        session.commit()
        #write_msg(event_id,'Buttons/Find.json',
        #          'ПОЛЬЗОВАТЕЛЬ УСПЕШНО ДОБАВЛЕН В ИЗБРАННОЕ')
        return True
    except (IntegrityError, InvalidRequestError):
        #write_msg(event_id,'Buttons/Find.json',
        #          'Пользователь уже в избранном.')
        return False


# Добавление пользователя в черный список
def add_to_checked_list(id_user, vk_id):
    try:
        new_user = CheckedList(
            vk_id=vk_id,
            id_user=id_user
        )
        db_user = session.query(CheckedList).filter_by(vk_id=vk_id).first()
        if db_user is not None:
            return

        session.add(new_user)
        session.commit()
        #Bot().write_msg(event_id,'Buttons/Find.json',
        #          'Пользователь успешно заблокирован.')
        return True
    except (IntegrityError, InvalidRequestError):
        #Bot().write_msg(event_id,'Buttons/Find.json',
         #         'Пользователь уже в черном списке.')
        return False


def search_user(vk_id):
    user=session.query(User).filter_by(vk_id=vk_id).first()
    if user is None:
        return 0
    else:
        return user


# проверят зареган ли пользователь бота в БД
def take_position(ids):

    current_user = session.query(User).filter_by(vk_id=ids).first()

    if current_user is None:
        return 0
    else:
        return current_user.position

def take_offset(user_id):
    try:
        offset = session.query(User.offset).filter(User.vk_id == user_id).first()
        if not offset:
            count = 0
        else:
            count = offset[0]
        return count
    except Exception as e:
        print(e)

def take_db_user(user_id):
    try:
        return session.query(User).filter(User.vk_id == user_id).first()
    except Exception as e:
        print(e)

def take_last_partner_vk_id():
    try:
        return session.query(CheckedList).order_by(CheckedList.id.desc()).first()
    except Exception as e:
        print(e)

def take_city(user_id):

    try:
        return session.query(User.city).filter(User.vk_id == user_id).first()
    except Exception as e:
        print(e)


def take_gender(user_id):

    try:
        return session.query(User.target_gender).filter(User.vk_id == user_id).first()
    except Exception as e:
        print(e)

def take_age_from(user_id):

    try:
        return session.query(User.age_from).filter(User.vk_id == user_id).first()
    except Exception as e:
        print(e)


def take_age_to(user_id):

    try:
        return session.query(User.age_from).filter(User.vk_id == user_id).first()
    except Exception as e:
        print(e)

#Возвращает идентификатор vk последнего партнера в базе данных
def get_partner_id():
    try:
        return session.query(CheckedList.vk_id).order_by(CheckedList.id.desc()).first()
    except Exception as e:
        print(e)

def update(user_id, target_table, **kwargs):

    try:
        db_user_id = take_db_user(user_id).id
        if target_table is User:
            session.query(target_table).filter(target_table.id == db_user_id).update({**kwargs})
        else:
            session.query(target_table).filter(target_table.id_user == db_user_id).update({**kwargs})
        session.commit()
    except Exception as e:
        print(e)



def create_tables():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        print(e)