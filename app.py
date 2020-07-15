import schedule, time, concurrent.futures
from datetime import datetime
from vk_bot import VkBot
# group_token = '***REMOVED***'


def make_post():
    try:
        local_stats, global_stats = vk.get_stats(get_global=True, get_local=True)
        current_date = datetime.fromtimestamp(global_stats['updated']/1000).strftime('%d.%m.%Y %H:%M')
        message = (
            f"Статистика по коронавирусу на {current_date}\n"
            "\nВ России:\n"
            f"Новых случаев: {local_stats['todayCases']}\n"
            f"Смертей сегодня: {local_stats['todayDeaths']}\n"
            f"Сегодня выздоровело: {local_stats['todayRecovered']}"
            f"Всего случаев: {local_stats['cases']}\n"
            f"Из них выздоровело: {local_stats['recovered']}\n"
            f"Всего смертей: {local_stats['deaths']}\n"
            f"Активных случаев: {local_stats['active']}\n"
            "\nВ мире:\n"
            f"Новых случаев: {global_stats['todayCases']}\n"
            f"Смертей сегодня: {global_stats['todayDeaths']}\n"
            f"Всего случаев: {global_stats['cases']}\n"
            f"Из них выздоровело: {global_stats['recovered']} ({global_stats['recovered']/(global_stats['cases']/100)}%)\n"
            f"Всего смертей: {global_stats['deaths']}\n"
            f"Акитвных случаев: {global_stats['active']}"
            f"Зараженных стран: {global_stats['affectedCountries']}"
        )
        vk.wall_post(message)
    except TypeError:
        time.sleep(900)
        make_post()

def messages_hander():
    messages = {
        'ru': ['рф', "ру", "россия", "в россии", 'ru', 'russia'],
        'world': ['мир', "в мире", 'world', 'worldwide'],
        'all': ['коронавирус', "коронавирус статистика", "covid", "все", "статистика"]
    }
    while True:
        try:
            event = vk.messages_loop()
            msg = event.message.text.lower().strip('[club***REMOVED***|@covid_stats] ')
            peer_id = event.message.peer_id
            out_msg = ""
            if msg in messages['ru'] or msg in messages['all']:
                local_stats = vk.get_stats(get_local=True)[0]
                out_msg += (
                    "\nВ России:\n"
                    f"Новых случаев: {local_stats['todayCases']}\n"
                    f"Смертей сегодня: {local_stats['todayDeaths']}\n"
                    f"Сегодня выздоровело: {local_stats['todayRecovered']}\n"
                    f"Всего случаев: {local_stats['cases']}\n"
                    f"Из них выздоровело: {local_stats['recovered']} ({round(local_stats['recovered']/(local_stats['cases']/100), 2)}%)\n"
                    f"Всего смертей: {local_stats['deaths']} ({round(local_stats['deaths']/(local_stats['cases']/100), 2)}%)\n"
                    f"Активных случаев: {local_stats['active']}\n"
                )
            if msg in messages['world'] or msg in messages['all']:
                global_stats = vk.get_stats(get_global=True)[0]
                out_msg += (
                    "\nВ мире:\n"
                    f"Новых случаев: {global_stats['todayCases']}\n"
                    f"Смертей сегодня: {global_stats['todayDeaths']}\n"
                    f"Всего случаев: {global_stats['cases']}\n"
                    f"Из них выздоровело: {global_stats['recovered']} ({round(global_stats['recovered']/(global_stats['cases']/100), 2)}%)\n"
                    f"Всего смертей: {global_stats['deaths']} ({round(global_stats['deaths']/(global_stats['cases']/100), 2)}%)\n"
                    f"Акитвных случаев: {global_stats['active']}\n"
                    f"Зараженных стран: {global_stats['affectedCountries']}"
                )
            if msg == 'начать':
                out_msg = (
                    'Привет! Я бот - коронавирус. Я могу сообщать тебе последнюю статистику по коронавирусу.\n\n'
                    'Чтобы начать, просто напиши одну из трех комманд: \n'
                    'ру - Узнать статистику в России.\n'
                    'мир - Узнать о ситуации в мире.\n'
                    'все - Статистика России и мира в одном сообщении.\n'
                )
            if out_msg != '': vk.send_message(peer_id, out_msg)
        except TypeError as ex:
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