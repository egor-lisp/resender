from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from threading import Thread, current_thread


class VkGroupListener:

    # Параметры листенера
    listen_new_events = False
    listening_thread_id = None

    # Параметры прослушки новых постов
    last_post_id = None  # Храним ID последних полученных постов
    on_new_post_function = None  # Функция которая вызывается при получение нового поста

    def __init__(self, group_token, group_id):
        # Создаем объект VKApi
        self.vk_session = VkApi(token=group_token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id=group_id)

    def _check_if_listen_thread_stopped(self):
        cur_thread_id = current_thread().ident
        is_stoped = not self.listen_new_events or cur_thread_id != self.listening_thread_id
        if is_stoped:
            print(f'Поток листенинга {cur_thread_id} остановлен')
        return is_stoped

    def _start_listen_new_events(self):
        self.listening_thread_id = current_thread().ident
        while True:
            if self._check_if_listen_thread_stopped():
                return
            for event in self.longpoll.listen():
                if self._check_if_listen_thread_stopped():
                    return
                if event.type == VkBotEventType.WALL_POST_NEW:
                    post_id = event.object['id']
                    # Сравниваем с последним полученным ID
                    if self.last_post_id is None or post_id > self.last_post_id:
                        self.last_post_id = post_id
                        if self.on_new_post_function:
                            self.on_new_post_function(event)

    def start_listen_new_events(self):
        self.listen_new_events = True
        t = Thread(target=self._start_listen_new_events)
        t.start()

    def stop_listen_new_events(self):
        self.listen_new_events = False
