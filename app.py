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
    def __init__(self, data_):
        log = logging.getLogger('bot')
        log_level = getattr(logging, data_['log'].upper(), 50)
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
        self.log = log
        self.log.info('Initializing VkBot class...')
        self.bot = VkBot(data_['user_token'], data_['group_token'], data_['group_id'])
        self.log.info('Running!')


    def make_post(self):
        try:
            self.log.info("Making a post...")
            local, world = api.get_stats(local = True, world = True)
            local_yesterday, global_yesterday = api.get_stats(local = True, world = True, yesterday = True)
            self.log.info('Got stats for post')

            message = 'Пишите в лс боту, чтобы получить последнюю статистику!\n'
            message += api.arrange_message(local, local_yesterday, 'в России')
            message += api.arrange_message(world, global_yesterday, 'в мире')

            self.log.info('Calling bot.wall_post()')
            self.bot.wall_post(message)
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
                event = self.bot.get_event()
                self.log.info('Got event with type %s', event.type)
                msg = re.sub(fr'\[{self.group_id}|.*\](,|) ', '', event.message['text'].lower()) # remove @ from message
                msg = msg.encode('cp1251', 'ignore').decode('cp1251').strip(' ') # remove all emojis and strip the space
                peer_id = event.message.peer_id
                self.log.info('Event message is "%s", peer id is %s', msg, peer_id)
                out_msg = ""

                if msg in messages['ru'] or msg in messages['all']:
                    self.log.info('Getting local stats for message...')
                    stats = api.get_stats(local = True)[0]
                    stats_yesterday = api.get_stats(local = True, yesterday = True)[0]
                    self.log.info('Got local stats!')
                    out_msg += api.arrange_message(stats, stats_yesterday, 'в России')

                if msg in messages['world'] or msg in messages['all']:
                    self.log.info('Getting global stats for message...')
                    stats = api.get_stats(world = True)[1]
                    stats_yesterday = api.get_stats(world = True, yesterday = True)[1]
                    self.log.info('Got global stats!')
                    out_msg += api.arrange_message(stats, stats_yesterday, 'в мире')

                if msg in messages['start'] or event.from_chat and msg == '':
                    out_msg = (
                        'Привет! Я бот - коронавирус. Я могу сообщать тебе последнюю статистику по коронавирусу.\n\n'
                        'Чтобы начать, просто напиши одну из трех комманд: \n'
                        'ру - Узнать статистику в России.\n'
                        'мир - Узнать о ситуации в мире.\n'
                        'все - Статистика России и мира в одном сообщении.\n'
                    )

                if out_msg != '': self.bot.send_message(peer_id, out_msg)
                else: self.bot.send_message(peer_id, 'Извини, но я тебя не понимаю. Напиши "помощь", чтобы получить список команд.')
            except TypeError:
                self.log.warning('Got TypeError in messages_handler()')
                self.bot.send_message(peer_id, 'Произошла ошибка. Повторите попытку позднее.')
            except:
                self.log.exception('')
                raise



def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(60)


def get_arguments():
    options = getopt.getopt(sys.argv[1:], "", ["log=", "group_id=", "group_token=", "user_token="])[0]
    out = {}
    for opt, arg in options:
        if opt == '--log':
            out.update({'log': arg})
        elif opt == '--group_id':
            out.update({'group_id': arg})
        elif opt == '--group_token':
            out.update({'group_token': arg})
        elif opt == '--user_token':
            out.update({'user_token': arg})
    return out


if __name__ == "__main__":
    with open('settings.yaml', 'r') as f:
        data = yaml.load(f, Loader = yaml.FullLoader)

    data.update(get_arguments())
    vk = VK(data)
    schedule.every().day.at('16:00').do(vk.make_post)

    with futures.ThreadPoolExecutor() as executor:
        t1 = executor.submit(schedule_loop)
        t2 = executor.submit(vk.messages_hander)