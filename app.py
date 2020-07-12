import schedule, time, concurrent.futures
from datetime import datetime
from vk_bot import VkBot
# group_token = '***REMOVED***'


def make_post():
    local_stats, global_stats = vk.get_stats(get_global=True, get_local=True)
    current_date = datetime.now().strftime('%d.%m.%Y')
    message = (
        f"Статистика по коронавирусу за {current_date}\n"
        "\nВ России:\n"
        f"Новых случаев: {local_stats['total_new_cases_today']}\n"
        f"Смертей сегодня: {local_stats['total_new_deaths_today']}\n"
        f"Всего случаев: {local_stats['total_cases']}\n"
        f"Из них выздоровело: {local_stats['total_recovered']}\n"
        f"Всего смертей: {local_stats['total_deaths']}\n"
        f"Уровень опасности: {local_stats['total_danger_rank']}\n"
        "\nВ мире:\n"
        f"Новых случаев: {global_stats['total_new_cases_today']}\n"
        f"Смертей сегодня: {global_stats['total_new_deaths_today']}\n"
        f"Всего случаев: {global_stats['total_cases']}\n"
        f"Из них выздоровело: {global_stats['total_recovered']}\n"
        f"Всего смертей: {global_stats['total_deaths']}\n"
        f"Зараженных стран: {global_stats['total_affected_countries']}"
    )
    vk.wall_post(message)

def messages_hander():
    messages = {
        'ru': ['рф', "ру", "россия", "в россии", 'ru', 'russia'],
        'world': ['мир', "в мире", 'world', 'worldwide'],
        'all': ['коронавирус', "коронавирус статистика", "covid", "все", "статистика"]
    }
    while True:
        event = vk.messages_loop()
        msg = event.message.text.lower().strip('[club***REMOVED***|@covid_stats] ')
        peer_id = event.message.peer_id
        out_msg = ""
        if msg in messages['ru'] or msg in messages['all']:
            stats = vk.get_stats(get_local=True)[0]
            out_msg += (
                f"\nВ России:\n"
                f"Новых случаев: {stats['total_new_cases_today']}\n"
                f"Смертей сегодня: {stats['total_new_deaths_today']}\n"
                f"Всего случаев: {stats['total_cases']}\n"
                f"Из них выздоровело: {stats['total_recovered']}\n"
                f"Всего смертей: {stats['total_deaths']}\n"
                f"Уровень опасности: {stats['total_danger_rank']}\n"
            )
        if msg in messages['world'] or msg in messages['all']:
            stats = vk.get_stats(get_global=True)[0]
            out_msg += (
                "\nВ мире:\n"
                f"Новых случаев: {stats['total_new_cases_today']}\n"
                f"Смертей сегодня: {stats['total_new_deaths_today']}\n"
                f"Всего случаев: {stats['total_cases']}\n"
                f"Из них выздоровело: {stats['total_recovered']}\n"
                f"Всего смертей: {stats['total_deaths']}\n"
                f"Зараженных стран: {stats['total_affected_countries']}"
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



def schedule_loop():
    while True:
        time.sleep(20)
        schedule.run_pending()


if __name__ == "__main__":
    vk = VkBot('***REMOVED***', '***REMOVED***', ***REMOVED***)
    schedule.every().day.at('16:00').do(make_post)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        t1 = executor.submit(schedule_loop)
        t2 = executor.submit(messages_hander)