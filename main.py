from bot_vkinder import *
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from time import sleep
from config import token, my_token, offset, line
from db import *
import json
import random

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text.lower()
            user_id = str(event.user_id)
            if request == 'поиск':
                creating_database()
                vkinder.send_message(event.user_id, f'Приветствую, {vkinder.get_name(event.user_id)}   можем попробовать поискать человека по твоему запросу.')
                vkinder.get_result_search(user_id)
                vkinder.send_message(event.user_id, f'Нашел для тебя несколько человек, пиши "еще" чтобы посмотреть следующего человека')
                vkinder.display_result(user_id, offset)
            elif request == 'еще':
                for i in line:
                    offset += 1
                    vkinder.display_result(user_id, offset)
                    break
            else:
                vkinder.send_message(event.user_id, 'такой команды у меня нет.')