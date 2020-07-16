from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json, requests

class VkBot:
    def __init__(self, user_token: str, group_token: str, group_id: int):
        self.group_id = group_id
        vk_session = VkApi(token = user_token, config_filename = '.vk_config.v2.json')
        self.vk = vk_session.get_api()
        self.group_session = VkApi(token=group_token, config_filename = '.vk_config.v2.json')
        self.group_vk = self.group_session.get_api()

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

class Api:
    @staticmethod
    def get_stats(local = False, world = False) -> dict:
        try:
            out = []
            if local: out.append(json.loads(requests.get('https://disease.sh/v3/covid-19/countries/Russia').text))
            if world: out.append(json.loads(requests.get('https://disease.sh/v3/covid-19/all').text))
            return out
        except json.JSONDecodeError:
            pass

    @staticmethod
    def arrange_message(stats, header) -> str:
        out_msg = ''
        recovered_percent = round(stats['recovered']/(stats['cases']/100), 2)
        deaths_percent = round(stats['deaths']/(stats['cases']/100), 2)
        return (
            f"\n{header}\n"
            f"Новых случаев: {stats['todayCases']}\n"
            f"Смертей сегодня: {stats['todayDeaths']}\n"
            f"Сегодня выздоровело: {stats['todayRecovered']}\n"
            f"Всего случаев: {stats['cases']}\n"
            f"Из них выздоровело: {stats['recovered']} ({recovered_percent}%)\n"
            f"Всего смертей: {stats['deaths']} ({deaths_percent}%)\n"
            f"Активных случаев: {stats['active']}\n"
        )


if __name__ == "__main__":
    pass