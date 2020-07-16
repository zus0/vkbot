import schedule, time, concurrent.futures
from datetime import datetime
from vk_bot import VkBot, Api as api


def make_post():
    try:
        local_stats, global_stats = api.get_stats(local=True, world=True)
        current_date = datetime.fromtimestamp(global_stats['updated']/1000).strftime('%d.%m.%Y %H:%M')
        message = f'Статистика по коронавирусу на {current_date}\nПишите в лс боту, чтобы получить последнюю статистику!n\n'
        message += api.arrange_message(local_stats, 'В России:')
        message += api.arrange_message(global_stats, 'В мире:')
        vk.wall_post(message)
    except TypeError:
        time.sleep(900)
        make_post()

def messages_hander():
    messages = {
        'ru': ['рф', "ру", "россия", "в россии", 'ru', 'russia'],
        'world': ['мир', "в мире", 'world', 'worldwide'],
        'all': ['коронавирус', "коронавирус статистика", "covid", "все", "статистика"],
        'start': ['начать', "помощь"]
    }
    while True:
        try:
            event = vk.messages_loop()
            prefix = '[club***REMOVED***|@covid_stats] '
            msg = event.message.text.lower().strip(prefix)
            peer_id = event.message.peer_id
            if prefix not in event.message.text: prefix = ''
            out_msg = ""
            if msg in messages['ru'] or msg in messages['all']:
                stats = api.get_stats(local = True)[0]
                out_msg += api.arrange_message(stats, 'В России:')
            if msg in messages['world'] or msg in messages['all']:
                stats = api.get_stats(world=True)[0]
                out_msg += api.arrange_message(stats, 'В мире:')
            if msg in messages['start'] or event.from_chat and msg == '':
                out_msg = (
                    'Привет! Я бот - коронавирус. Я могу сообщать тебе последнюю статистику по коронавирусу.\n\n'
                    'Чтобы начать, просто напиши одну из трех комманд: \n'
                    'ру - Узнать статистику в России.\n'
                    'мир - Узнать о ситуации в мире.\n'
                    'все - Статистика России и мира в одном сообщении.\n'
                )
            if out_msg != '': vk.send_message(peer_id, out_msg)
            else: vk.send_message(peer_id, f'Извини, но я тебя не понимаю. Напиши "{prefix}помощь", чтобы получить список команд.')
        except TypeError:
            vk.send_message(peer_id, 'Произошла ошибка. Повторите попытку позднее.')



def schedule_loop():
    while True:
        schedule.run_pending()
        time.sleep(40)


if __name__ == "__main__":
    vk = VkBot('***REMOVED***', '***REMOVED***', ***REMOVED***)
    schedule.every().day.at('16:00').do(make_post)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        t1 = executor.submit(schedule_loop)
        t2 = executor.submit(messages_hander)