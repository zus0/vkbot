import json
import logging
import requests
from datetime import datetime
from vk_api import VkApi, keyboard
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

class VkBot:
    def __init__(self, user_token: str, group_token: str, group_id: int):
        self.log = logging.getLogger('bot.vk_bot')
        self.group_id = group_id

        vk_session = VkApi(token = user_token, config_filename = '.vk_config.v2.json')
        group_session = VkApi(token = group_token, config_filename = '.vk_config.v2.json')

        self.log.info('Authentication...')
        self.vk = vk_session.get_api()
        self.log.info('User authenticated!')
        self.group_vk = group_session.get_api()
        self.log.info('Group authenticated!')
        self.longpoll = VkBotLongPoll(group_session, self.group_id)
        self.log.info('Got longpoll')

        self.kb = keyboard.VkKeyboard()
        for option in ["Россия 🇷🇺", "Мир 🌎", "Все 📊"]: self.kb.add_button(option, color='primary')

    def wall_post(self, message):
        post_id = self.vk.wall.post(owner_id = -self.group_id, message = message, from_group = True)['post_id']
        self.vk.wall.pin(owner_id = -self.group_id, post_id = post_id)
        self.log.info("Wall post with id of %s", post_id)

    def send_message(self, peer_id, message):
        kb = (self.kb.get_keyboard() if peer_id < 2000000000 else None)
        message_id = self.group_vk.messages.send(peer_id = peer_id, message = message, random_id = 0, keyboard = kb)
        self.log.info("Sent message with id %s to %s", message_id, peer_id)
    
    def get_event(self):
        while True:
            try:
                for event in self.longpoll.listen():
                    self.log.debug("Got event with type %s", event.type)
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        return event
            except requests.ReadTimeout:
                self.log.warning('Request timeout in longpoll.listen()')
            except requests.exceptions.ConnectionError:
                self.log.warning('Connection Error in longpoll.listen()')
            except:
                self.log.exception('Exception in longpoll.listen()')

class Api:
    log = logging.getLogger('vk.Api')

    @classmethod
    def get_stats(cls, local = False, world = False, yesterday = False) -> dict:
        out = [[], []]
        yesterday = ('true' if yesterday else 'false')
        try:
            if local: out[0] = json.loads(requests.get('https://disease.sh/v3/covid-19/countries/Russia', params={"yesterday": yesterday}).text)
            if world: out[1] = json.loads(requests.get('https://disease.sh/v3/covid-19/all', params={"yesterday": yesterday}).text)
        except json.JSONDecodeError:
            cls.log.warning('Unable to decode API data')
        cls.log.debug(out)
        return out

    @classmethod
    def arrange_message(cls, stats, stats_yesterday, header) -> str:
        deaths_percent = round(stats['deaths']/(stats['cases']/100), 2)
        recovered_percent = round(stats['recovered']/(stats['cases']/100), 2)
        current_date = datetime.fromtimestamp(stats['updated']/1000).strftime('%d.%m.%Y %H:%M')

        cases_diff = "{:+}".format(stats['todayCases'] - stats_yesterday['todayCases'])
        deaths_diff = "{:+}".format(stats['todayDeaths'] - stats_yesterday['todayDeaths'])
        recovered_diff = "{:+}".format(stats['todayRecovered'] - stats_yesterday['todayRecovered'])

        out = f'\nСтатистика {header} на {current_date}:\n'

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
            f"Активных случаев: {stats['active']}\n"
        )

        cls.log.debug(out)
        return out


if __name__ == "__main__":
    pass