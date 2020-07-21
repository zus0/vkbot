from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime
import json
import requests
import logging

class VkBot:
    def __init__(self, user_token: str, group_token: str, group_id: int):
        self.group_id = group_id
        vk_session = VkApi(token = user_token, config_filename = '.vk_config.v2.json')
        self.vk = vk_session.get_api()
        self.group_session = VkApi(token = group_token, config_filename = '.vk_config.v2.json')
        self.group_vk = self.group_session.get_api()
        self.longpoll = VkBotLongPoll(self.group_session, self.group_id)

    def wall_post(self, message):
        post_id = self.vk.wall.post(owner_id = -self.group_id, message = message, from_group = True)['post_id']
        self.vk.wall.pin(owner_id = -self.group_id, post_id = post_id)
        logging.info("Wall post at %s with id of %s", datetime.now().strftime('%d.%m.%Y %H:%M'), post_id)

    def send_message(self, peer_id, message):
        self.group_vk.messages.send(peer_id = peer_id, message = message, random_id = 0)
    
    def get_event(self):
        while True:
            try:
                for event in self.longpoll.listen():
                    logging.info("Got event at %s", datetime.now().strftime('%d.%m.%Y %H:%M'))
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        return event
            except requests.ReadTimeout:
                logging.warning('Request timeout in longpoll.listen()')

class Api:
    @staticmethod
    def get_stats(local = False, world = False, yesterday = False) -> list:
        out = []
        yesterday = ('true' if yesterday else 'false')
        try:
            if local: out.append(json.loads(requests.get('https://disease.sh/v3/covid-19/countries/Russia', params={"yesterday": yesterday}).text))
            if world: out.append(json.loads(requests.get('https://disease.sh/v3/covid-19/all', params={"yesterday": yesterday}).text))
        except json.JSONDecodeError:
            logging.warning('Unable to decode API data')
        logging.debug(out)
        return out

    @staticmethod
    def arrange_message(stats, stats_yesterday, header) -> str:
        out = f'\n{header}\n'
        cases_diff = "{:+}".format(stats['todayCases'] - stats_yesterday['todayCases'])
        deaths_diff = "{:+}".format(stats['todayDeaths'] - stats_yesterday['todayDeaths'])
        recovered_diff = "{:+}".format(stats['todayRecovered'] - stats_yesterday['todayRecovered'])
        active_diff = "{:+}".format(stats['active'] - stats_yesterday['active'])
        recovered_percent = round(stats['recovered']/(stats['cases']/100), 2)
        deaths_percent = round(stats['deaths']/(stats['cases']/100), 2)
        if stats['todayCases'] == 0:
            out += 'На сегодня нет новой информации.\n'
        else:
            out += (
                f"Новых случаев: {stats['todayCases']} ({cases_diff})\n"
                f"Смертей сегодня: {stats['todayDeaths']} ({deaths_diff})\n"
                f"Сегодня выздоровело: {stats['todayRecovered']} ({recovered_diff})\n"
            )
        out += (
            f"Всего случаев: {stats['cases']}\n"
            f"Из них выздоровело: {stats['recovered']} ({recovered_percent}%)\n"
            f"Всего смертей: {stats['deaths']} ({deaths_percent}%)\n"
            f"Активных случаев: {stats['active']} ({active_diff})\n"
        )
        logging.debug(out)
        return out


if __name__ == "__main__":
    pass