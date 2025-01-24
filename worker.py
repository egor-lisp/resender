from config import ConfigManager
from models import Post, Video, Photo
import utils
from vk_listener import VkGroupListener
from socials.ok import OK
from vk_api.bot_longpoll import VkBotEvent
import os
from telebot import TeleBot

cm = ConfigManager()
LOADED_FOLDER = 'loaded_files'


def parse_vk_post(event: VkBotEvent, download_photo=False, download_video=False):
    # Получаем ссылку на пост
    post_id = event.object['id']
    owner_id = event.group_id
    wall_id = f'wall-{owner_id}_{post_id}'
    # Получаем контент поста
    text = event.object.get('text', '')
    text = utils.replace_allias_vk_urls(text)

    attachments = event.object.get('attachments', [])
    photos = []  # Пути к фото на локальном ПК
    videos = []  # Пути к видео на локальном ПК
    for attach in attachments:

        if attach.get('type') == 'photo':
            max_size_elem = max(
                attach['photo']['sizes'],
                key=lambda size: (size['width'], size['height'])
            )
            photo_url = max_size_elem['url']
            if download_photo:
                file_path = f'{LOADED_FOLDER}/{wall_id}-{utils.random_string(10)}.jpg'
                success = utils.load_photo_by_url(photo_url, file_path)
                if success:
                    photos.append(Photo(
                        url=photo_url, is_loaded=True, photo_file_path=file_path
                    ))
            else:
                photos.append(Photo(url=photo_url))

        if attach.get('type') == 'video':
            title = attach['video']['title']
            owner_id = attach['video']['owner_id']
            video_id = attach['video']['id']
            video_url = f'https://vk.com/video{owner_id}_{video_id}'
            if download_video:
                file_path = f'{LOADED_FOLDER}/{owner_id}_{video_id}.mp4'
                success = utils.download_vk_video(video_url, file_path)
                if success:
                    videos.append(Video(
                        url=video_url, title=title,
                        is_loaded=True, video_file_path=file_path
                    ))
            else:
                videos.append(Video(url=video_url, title=title))

    post = Post(
        url=f'https://vk.com/{wall_id}', text=text,
        photos=photos, videos=videos
    )
    return post


def send_tg_report(text, disable_preview=True):
    bot = TeleBot(cm.tg_bot_token)
    for user_id in cm.tg_admin_ids:
        bot.send_message(user_id, text, disable_web_page_preview=disable_preview)


class Worker:

    is_work = False

    listener: VkGroupListener
    ok: OK

    def on_new_vk_post(self, event: VkBotEvent):
        print(event)

        try:
            post_preview = parse_vk_post(event)
        except Exception as ex:
            send_tg_report(f'Ошибка в парсинге поста вк https://vk.com/club/{cm.vk_group_id}: {ex}')
            return

        report_text = \
            f'Новый пост в группе вк https://vk.com/club/{cm.vk_group_id}\n' \
            f'Кол-во букв в тексте поста: {len(post_preview.text)}\n' \
            f'Кол-во картинок в посте: {len(post_preview.photos)}\n' \
            f'Кол-во видео в посте: {len(post_preview.videos)}\n\n' \
            f'После загрузки всех картинок и видео пост будет переслан на другие площадки. Это может занять некоторое время.'
        send_tg_report(report_text)

        try:
            post = parse_vk_post(event, download_photo=True, download_video=True)
        except Exception as ex:
            send_tg_report(f'Ошибка в парсинге картинок или видео поста вк https://vk.com/club/{cm.vk_group_id}: {ex}')
            return

        report_text = f'Пост из вк https://vk.com/club/{cm.vk_group_id}\n\n'

        if cm.ok_resend:
            try:
                res = self.ok.add_post(post)
                if 'error' in res.text:
                    report_text += f'❌ Одноклассники: неудачный запрос на размещение поста. Текст ответа: {res.text}\n\n'
                else:
                    post_id = res.text.split('"')[1].split('"')[0]
                    post_url = f'https://ok.ru/group/{cm.ok_group_id}/topic/{post_id}'
                    report_text += f'✅ Одноклассники: успешно переслан пост, ссылка: {post_url}\n\n'
            except Exception as ex:
                report_text += f'❌ Одноклассники: исключение скрипта при пересылке поста. Текст ошибки: {ex}\n\n'

        send_tg_report(report_text)

        # Удаляем материалы поста с локального пк
        for file_path in [photo.file_path for photo in post.photos]:
            os.remove(file_path)
        for file_path in [video.file_path for video in post.videos]:
            os.remove(file_path)

    def start(self):
        if self.is_work:
            return

        self.is_work = True
        cm.read_config()  # Читаем данные

        # Провеярем что все настройки указаны
        if not cm.vk_token:
            return {'start': False, 'message': 'Необходимо указать токен вк.'}
        if not cm.vk_group_id:
            return {'start': False, 'message': 'Необходимо указать ID группы вк.'}

        if cm.ok_resend:
            if not cm.ok_access_token:
                return {'start': False, 'message': 'Необходимо указать OK_ACCESS_TOKEN'}
            if not cm.ok_app_key:
                return {'start': False, 'message': 'Необходимо указать OK_APP_KEY'}
            if not cm.ok_app_secret:
                return {'start': False, 'message': 'Необходимо указать OK_APP_SECRET'}
            if not cm.ok_group_id:
                return {'start': False, 'message': 'Необходимо указать ID группы ОК'}

        # Создаем объекты соц. сетей куда мы будем пересылать посты
        self.ok = OK(
            access_token=cm.ok_access_token, app_key=cm.ok_app_key,
            app_secret=cm.ok_app_secret, group_id=cm.ok_group_id
        )

        # Создаем и настраиваем long poll api у вк для получения новых постов
        self.listener = VkGroupListener(
            group_token=cm.vk_token, group_id=cm.vk_group_id
        )
        self.listener.on_new_post_function = self.on_new_vk_post
        self.listener.start_listen_new_events()
        return {'start': True}

    def stop(self):
        if not self.is_work:
            return
        self.listener.stop_listen_new_events()
        self.is_work = False


if __name__ == '__main__':
    Worker().start()
