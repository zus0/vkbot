import schedule, time
from datetime import datetime
from vk_bot import VkBot
vk = VkBot('***REMOVED***', ***REMOVED***)


def make_post():
    local_stats, global_stats = vk.get_info()
    current_date = datetime.now().strftime('%d.%m.%Y')
    message = (f"Статистика по коронавирусу за {current_date}\n"
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
schedule.every().day.at('19:00').do(make_post)

def main():
    while True:
        time.sleep(20)
        schedule.run_pending()
    
if __name__ == "__main__":
    main()