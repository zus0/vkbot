import schedule
import time
import yaml
import re
import logging
from concurrent import futures
from datetime import datetime
from vk_bot import VkBot, Api as api

def initialize_logging():
    logging.basicConfig(filename='bot.log', level = logging.INFO)
    logging.info('Started!')

def make_post():
    try:
        local, world = api.get_stats(local = True, world = True)
        local_yesterday, global_yesterday = api.get_stats(local = True, world = True, yesterday = True)
        current_date = datetime.fromtimestamp(world['updated']/1000).strftime('%d.%m.%Y %H:%M')
        message = f'Статистика по коронавирусу на {current_date}\nПишите в лс боту, чтобы получить последнюю статистику!\n\n'
        message += api.arrange_message(local, local_yesterday, 'В России:')
        message += api.arrange_message(world, global_yesterday, 'В мире:')
        vk.wall_post(message)
    except TypeError:
        logging.warning('Got TypeError in make_post()')
        time.sleep(900)
        make_post()

def messages_hander():
    messages = {
        'ru': ['рф', "ру", "россия", 'ru', 'russia'],
        'world': ['мир', "в мире", 'world', 'worldwide'],
        'all': ['коронавирус', "covid", "все", "статистика"],
        'start': ['начать', "помощь"]
    }
    while True:
        try:
            event = vk.get_event()
            msg = re.sub(fr'\[{data["group_id"]}|.*\](,|) ', '', event.message['text'].lower()) # remove @ from message
            msg = msg.encode('cp1251', 'ignore').decode('cp1251').strip(' ') # remove all emojis and strip the space
            peer_id = event.message.peer_id
            out_msg = ""
            if msg in messages['ru'] or msg in messages['all']:
                stats = api.get_stats(local = True)[0]
                stats_yesterday = api.get_stats(local = True, yesterday = True)[0]
                out_msg += api.arrange_message(stats, stats_yesterday, 'В России:')
            if msg in messages['world'] or msg in messages['all']:
                stats = api.get_stats(world = True)[0]
                stats_yesterday = api.get_stats(world = True, yesterday = True)[0]
                out_msg += api.arrange_message(stats, stats_yesterday, 'В мире:')
            if msg in messages['start'] or event.from_chat and msg == '':
                out_msg = (
                    'Привет! Я бот - коронавирус. Я могу сообщать тебе последнюю статистику по коронавирусу.\n\n'
                    'Чтобы начать, просто напиши одну из трех комманд: \n'
                    'ру - Узнать статистику в России.\n'
                    'мир - Узнать о ситуации в мире.\n'
                    'все - Статистика России и мира в одном сообщении.\n'
                )
            if out_msg != '': vk.send_message(peer_id, out_msg)
            else: vk.send_message(peer_id, 'Извини, но я тебя не понимаю. Напиши "помощь", чтобы получить список команд.')
        except TypeError:
            logging.warning('Got TypeError in messages_handler()')
            vk.send_message(peer_id, 'Произошла ошибка. Повторите попытку позднее.')



def schedule_loop():
    while True:
        logging.info("Schedule at %s", datetime.now().strftime('%d.%m.%Y %H:%M'))
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    initialize_logging()
    with open('data.yaml', 'r') as f:
        data = yaml.load(f, Loader = yaml.FullLoader)
    vk = VkBot(data['user_token'], data['group_token'], data['group_id'])
    schedule.every().day.at('16:00').do(make_post)
    
    with futures.ThreadPoolExecutor() as executor:
        t1 = executor.submit(schedule_loop)
        t2 = executor.submit(messages_hander)
