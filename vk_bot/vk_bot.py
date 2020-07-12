from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json, requests


class VkBot:
    def __init__(self, token: str, group_token: str, group_id: int):
        self.group_id = group_id
        vk_session = VkApi(token = token, config_filename = '.vk_config.v2.json')
        self.vk = vk_session.get_api()
        self.group_session = VkApi(token=group_token, config_filename = '.vk_config.v2.json')
        self.group_vk = self.group_session.get_api()

    def get_stats(self, get_local = False, get_global = False) -> dict:
        out = []
        if get_local: out.append(json.loads(requests.get('https://api.thevirustracker.com/free-api?countryTotal=RU').text)['countrydata'][0])
        if get_global: out.append(json.loads(requests.get('https://api.thevirustracker.com/free-api?global=stats').text)['results'][0])
        return out

    def wall_post(self, message):
        post_id = self.vk.wall.post(owner_id = -self.group_id, message = message, from_group = True)['post_id']
        self.vk.wall.pin(owner_id = -self.group_id, post_id = post_id)

    def send_message(self, peer_id, message):
        self.group_vk.messages.send(peer_id = peer_id, message = message, random_id = 0)
    
    def messages_loop(self):
        longpoll = VkBotLongPoll(self.group_session, self.group_id)
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                return event


if __name__ == "__main__":
    pass