import vk_api
import time

# Ваш токен доступа (получить на https://vkhost.github.io/)
ACCESS_TOKEN = "ваш токен"


def mark_messages_as_read():
    """Отмечает все непрочитанные сообщения как прочитанные"""
    vk_session = vk_api.VkApi(token=ACCESS_TOKEN)
    vk = vk_session.get_api()

    try:
        # Получаем список непрочитанных диалогов
        conversations = vk.messages.getConversations(filter='unread', count=200)

        if conversations['count'] == 0:
            print("Нет непрочитанных сообщений")
            return

        print(f"Найдено непрочитанных диалогов: {conversations['count']}")

        # Проходим по каждому диалогу и отмечаем как прочитанное
        for item in conversations['items']:
            peer_id = item['conversation']['peer']['id']

            # Отмечаем сообщения как прочитанные
            vk.messages.markAsRead(peer_id=peer_id)
            print(f"Диалог {peer_id} отмечен как прочитанный")

            # Небольшая задержка, чтобы не превысить лимиты API
            time.sleep(0.5)

        print("Все сообщения отмечены как прочитанные!")

    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка API: {e}")


def auto_read_loop(interval=60):
    """Автоматически проверяет и читает сообщения с заданным интервалом"""
    print(f"Запущен автоматический режим (проверка каждые {interval} сек)")

    while True:
        try:
            mark_messages_as_read()
            print(f"Следующая проверка через {interval} секунд...")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nОстановлено пользователем")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(interval)


if __name__ == "__main__":
    # Выберите режим работы:

    # Разовое прочтение всех сообщений
    mark_messages_as_read()

    # Или автоматический режим (раскомментируйте)
    # auto_read_loop(interval=60)  # Проверка каждые 60 секунд