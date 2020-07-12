from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
import json, requests

class VkBot:
    def __init__(self, token: str, group_id: int):
        self.group_id = group_id
        vk_session = VkApi(token = token, config_filename = '.vk_config.v2.json')
        self.vk = vk_session.get_api()

    def get_info(self):
        local_stats = json.loads(requests.get('https://api.thevirustracker.com/free-api?countryTotal=RU').text)['countrydata'][0]
        global_stats = json.loads(requests.get('https://api.thevirustracker.com/free-api?global=stats').text)['results'][0]
        return local_stats, global_stats

    def wall_post(self, message):
        post_id = self.vk.wall.post(owner_id = -self.group_id, message = message, from_group = True)['post_id']
        self.vk.wall.pin(owner_id = -self.group_id, post_id = post_id)
    
    def messages_loop(self):
        session = VkApi(token='***REMOVED***')
        longpoll = VkLongPoll(session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                print(event.message)


if __name__ == "__main__":
    pass