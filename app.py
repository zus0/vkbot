import getopt
import logging
import re
import sys
import time
import schedule
import yaml
from concurrent import futures
from vk_bot import VkBot, Api as api

class VK:
    def __init__(self, data_, log_level):
        log = logging.getLogger('bot')
        log.setLevel(log_level)
        fmt = logging.Formatter('[%(asctime)s] %(levelname)s: %(name)s: %(message)s')

        fh = logging.FileHandler('bot.log', 'w')
        fh.setFormatter(fmt)
        log.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        ch.setLevel(logging.WARNING)
        log.addHandler(ch)

        self.group_id = data_['group_id']
        self.vk = VkBot(data_['user_token'], data_['group_token'], data_['group_id'])
        self.log = log


    def make_post(self):
        try:
            local, world = api.get_stats(local = True, world = True)
            local_yesterday, global_yesterday = api.get_stats(local = True, world = True, yesterday = True)

            message = 'Пишите в лс боту, чтобы получить последнюю статистику!\n'
            message += api.arrange_message(local, local_yesterday, 'в России')
            message += api.arrange_message(world, global_yesterday, 'в мире')

            self.vk.wall_post(message)
        except:
            self.log.exception('')


    def messages_hander(self):
        messages = {
            'ru': ['рф', "ру", "россия", 'ru', 'russia'],
            'world': ['мир', "в мире", 'world', 'worldwide'],
            'all': ['коронавирус', "covid", "все", "статистика"],
            'start': ['начать', "помощь"]
        }

        while True:
            try:
                event = self.vk.get_event()
                self.log.info('Got event with type %s', event.type)
                msg = re.sub(fr'\[{self.group_id}|.*\](,|) ', '', event.message['text'].lower()) # remove @ from message
                msg = msg.encode('cp1251', 'ignore').decode('cp1251').strip(' ') # remove all emojis and strip the space
                peer_id = event.message.peer_id
                self.log.info('Event message is %s, peer id is %s', msg, peer_id)
                out_msg = ""

                if msg in messages['ru'] or msg in messages['all']:
                    stats = api.get_stats(local = True)[0]
                    stats_yesterday = api.get_stats(local = True, yesterday = True)[0]
                    out_msg += api.arrange_message(stats, stats_yesterday, 'в России')

                if msg in messages['world'] or msg in messages['all']:
                    stats = api.get_stats(world = True)[1]
                    stats_yesterday = api.get_stats(world = True, yesterday = True)[1]
                    out_msg += api.arrange_message(stats, stats_yesterday, 'в мире')

                if msg in messages['start'] or event.from_chat and msg == '':
                    out_msg = (
                        'Привет! Я бот - коронавирус. Я могу сообщать тебе последнюю статистику по коронавирусу.\n\n'
                        'Чтобы начать, просто напиши одну из трех комманд: \n'
                        'ру - Узнать статистику в России.\n'
                        'мир - Узнать о ситуации в мире.\n'
                        'все - Статистика России и мира в одном сообщении.\n'
                    )

                if out_msg != '': self.vk.send_message(peer_id, out_msg)
                else: self.vk.send_message(peer_id, 'Извини, но я тебя не понимаю. Напиши "помощь", чтобы получить список команд.')
            except TypeError:
                self.log.warning('Got TypeError in messages_handler()')
                self.vk.send_message(peer_id, 'Произошла ошибка. Повторите попытку позднее.')
            except:
                self.log.exception('')
                raise


    def schedule_loop(self):
        while True:
            try:
                self.log.debug("Schedule loop")
                schedule.run_pending()
                time.sleep(60)
            except:
                self.log.exception('')
                raise


def get_arguments():
    options = getopt.getopt(sys.argv[1:], "", ["log="])[0]
    numeric_level = 30
    out = {'numeric_level': numeric_level}
    for opt, arg in options:
        if opt == '--log':
            out['numeric_level'] = getattr(logging, arg.upper(), numeric_level)
    return out


if __name__ == "__main__":
    with open('data.yaml', 'r') as f:
        data = yaml.load(f, Loader = yaml.FullLoader)

    args = get_arguments()
    vk = VK(data, args['numeric_level'])
    schedule.every().day.at('16:00').do(vk.make_post)

    with futures.ThreadPoolExecutor() as executor:
        t1 = executor.submit(vk.schedule_loop)
        t2 = executor.submit(vk.messages_hander)