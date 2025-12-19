import vk_api
import time

ACCESS_TOKEN = "ваш_токен_здесь"

def mark_messages_as_read():
    vk_session = vk_api.VkApi(token=ACCESS_TOKEN)
    vk = vk_session.get_api()

    try:
        conversations = vk.messages.getConversations(filter='unread', count=200)

        if conversations['count'] == 0:
            print("Нет непрочитанных сообщений")
            return

        print(f"Найдено непрочитанных: {conversations['count']}")

        for item in conversations['items']:
            peer_id = item['conversation']['peer']['id']
            vk.messages.markAsRead(peer_id=peer_id)
            print(f"Диалог {peer_id} прочитан")
            time.sleep(0.5)

        print("Готово!")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    mark_messages_as_read()