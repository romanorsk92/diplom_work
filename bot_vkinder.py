import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from config import my_token, token, offset, line
import json
import datetime
import time
import random
from db import *


class Bot:
    def __init__(self, my_token, api_version, url='https://api.vk.com/'):
        print('бот создан')
        self.vk_group = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk_group)
        self.url = url
        self.api_version = api_version
        self.my_token = my_token
        

        

    def main_params(self):
        return {
            "access_token": self.my_token,
            "v": self.api_version
        }

    def send_message(self, user_id, message):
        """метод для отправки сообщений"""
        self.vk_group.method('messages.send', {'user_id': user_id,
                                               'message': message,
                                               'random_id': 0
                                               })

    def get_user_info(self, user_id):
        """Получение необходимой для поиска информации"""
        params = {
            'user_ids': user_id,
            'fields': 'city, bdate, sex, relation, age'
        }
        user_info = requests.get(
            f'{self.url}/method/users.get', params={**params, **self.main_params()}).json()
        time.sleep(0.35)
        response = user_info['response'][0]

        #try:
            #if user_info.status_code == 200:
                #response = user_info.json()['response'][0]
                #print(response)
        #except KeyError:
            #self.send_message(
                #user_id, 'К сожалению что-то пошло не так. Попробуйте еще раз!')

        search_params = {
            'user_id' : user_id,
        }
        user_city = response['city']['title']
        # Проверка наличия города в запрошенных данных
        if 'city' in response:
            search_params['city'] = response['city']['id']
        else:  # если город отсутствует запрашиваем город через диалог с пользователем.
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        user_city = event.text
                        self.send_message(
                            user_id, 'У вас не указан или скрыт город. Введите сюда пожалуйста город, в котором вы живете.')
                        params = {
                            'access_token' : my_token,
                            'q' : f'{user_city}',
                            'need_all' : 1
                        }
                        response = requests.get(
                            f'{self.url}/method/database.getCities', params={**params, **self.main_params()}).json()
                        list_cities = response['response']['items']
                        for el in list_cities:
                            found_title = i.get('title')
                            if found_title == user_city:
                                found_id = i.get('id')
                                search_params['city'] = found_id
                                break

        user_age = response['bdate']
        # Проверяем наличие даты рождения в полученных данных от пользователя И что дата рождения указана полностью.
        if ('bdate' in response) and (len(user_age.split('.')) == 3):
            # Получаем год рождения и высчитываем возраст.
            search_age = datetime.date.today().year - \
                int(user_age.split('.')[2])
            search_params['age'] = search_age
        else:  # Если дата указана не полностью или скрыта, запрашиваем возраст у пользователя в диалоге.
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        user_age = event.text
                        self.send_message(
                            event.user_id, 'укажите свой возраст')
                        search_params['age'] = user_age
                        break

        user_sex = response['sex']
        if user_sex == 1:  # Если пол женский
            # то выставляем для поиска --мужской пол.
            search_params['sex'] = user_sex = 2
        elif user_sex == 2:  # Если пол мужской.
            # то для поиска выставляем --женский пол.
            search_params['sex'] = user_sex = 1
        else:  # Если пол скрыт. То запрашиваем у пользователя его пол и выставляем для поиска противоположный.
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        user_sex = event.text
                        self.send_message(
                            event.user_id, ' к сожалению у вас не указан пол, а он необходим для поиска. Если ваш пол женский введите число 1, а если мужской введите число 2.')
                        if user_sex == 1:
                            search_params['sex'] = user_sex = 2
                        elif user_sex == 2:
                            search_params['sex'] = user_sex = 1

        if response:   # по умолчанию семейное положение -в активном поиске.
            search_params['relation'] = 6
            #print(search_params)
        return search_params

    def get_name(self, user_id):
        """Получение имени пользователя для обращения к нему"""
        params = {
            'user_ids' : user_id,
            'fields' : 'first_name, last_name'
        }
        response = requests.get(
            f'{self.url}/method/users.get', params={**params, **self.main_params()})
        try:
            if response.status_code == 200:
                name = response.json()['response'][0]['first_name']
                return name
        except:
            self.send_message(event.user_id, 'К сожалению что-то пошло не так!')

    def get_result_search(self, user_id):
        """метод выполняющий поиск людей по полученным параметрам """
        search_options = {
            'city_id' : str(self.get_user_info(user_id)['city']),
            'sex' : self.get_user_info(user_id)['sex'],
            'status' : self.get_user_info(user_id)['relation'],
            'has_photo' : 1,
            'age_from' : self.get_user_info(user_id)['age'] - 3,
            'age_to' : self.get_user_info(user_id)['age'] +3,
            'is_closed' : False,
            'sort' : 0,
            'fields' : 'id, bdate, first_name, last_name, age, city, relation',
            'count' : 1000
        }
        response = requests.get(
            f'{self.url}/method/users.search', params={**search_options, **self.main_params()}).json()
        
        for user in response['response']['items']:
            first_name = user.get('first_name')
            last_name = user.get('last_name')
            vk_id = str(user.get('id'))
            vk_link = 'vk.com/id'+str(user.get('id'))
            insert_data_users(first_name, last_name, vk_id, vk_link)
        return self.send_message(user_id, 'Поиск завершен, обрабатываем результат.')

    def get_photos_ids(self, user_id):
        '''получение фотографий'''
        params = {
            'owner_id' : user_id,
            'album_id' : 'profile',
            'extended' : 1
        }
        response = requests.get(
            f'{self.url}/method/photos.get', params={**params, **self.main_params()}).json()
        time.sleep(0.35)
        photos = {}
        result = response['response']['items']
        for photo in result:
            photo_id = str(photo.get('id'))
            likes = photo.get('likes')
            comments = photo.get('comments')
            if likes.get('count'):
                likes_count = likes.get('count')
            if comments.get('count'):
                comments_count = comments.get('count')
                photos[likes_count + comments_count] = photo_id
        list_ids = sorted(photos.items(), reverse = True)
        return list_ids

    def get_photo_1(self, user_id):
        list = self.get_photos_ids(user_id)
        count = 0
        for photo in list:
            count += 1
            if count == 1:
                return photo[1]

    def get_photo_2(self, user_id):
        list = self.get_photos_ids(user_id)
        count = 0
        for photo in list:
            count += 1
            if count == 2:
                return photo[1]

    def get_photo_3(self, user_id):
        list = self.get_photos_ids(user_id)
        count = 0
        for photo in list:
            count += 1
            if count == 3:
                return photo[1]

    def send_photo_1(self, user_id, message, offset):
        self.vk_group.method('messages.send', {'user_id' : user_id,
            'access_token' : my_token,
            'message' : message,
            'attachment': f'photo{self.get_user_id(offset)}_{self.get_photo_1(self.get_user_id(offset))}',
            'random_id' : 0
        })        

    def send_photo_2(self, user_id, message, offset):
        self.vk_group.method('messages.send', {'user_id' : user_id,
            'message' : message,
            'attachment': f'photo{self.get_user_id(offset)}_{self.get_photo_2(self.get_user_id(offset))}',
            'random_id' : 0
        }) 

    def send_photo_3(self, user_id, message, offset):
        self.vk_group.method('messages.send', {'user_id' : user_id,
            'message' : message,
            'attachment': f'photo{self.get_user_id(offset)}_{self.get_photo_3(self.get_user_id(offset))}',
            'random_id' : 0
        }) 

    def display_result(self, user_id, offset):
        self.send_message(user_id, self.display_user_info(offset))
        self.get_user_id(offset)
        insert_data_seen_users(self.get_user_id(offset), offset)
        self.get_photos_ids(self.get_user_id(offset))
        self.send_photo_1(user_id, 'Фото №1', offset)
        self.send_photo_2(user_id, "фото №2", offset)
        self.send_photo_3(user_id, 'Фото № 3', offset)
        self.send_message(user_id, 'Больше фото нет!')
    def display_user_info(self, offset):
        info_person = select(offset)
        list_person = []
        for user in info_person:
            list_person.append(user)
        return f'{list_person[0]} {list_person[1]} ссылка- {list_person[3]}'

    def get_user_id(self, offset):
        info_person = select(offset)
        list_person = []
        for id in info_person:
            list_person.append(id)
        return str(list_person[2])


vkinder = Bot(my_token=my_token, api_version='5.131')
