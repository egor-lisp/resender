from socials.ok import OK
from config import ConfigManager
from models import Post, Video
import utils

cm = ConfigManager()
cm.read_config()

utils.download_vk_video('https://vk.com/artursitapodcast?z=video-40378105_456239245%2F8d2c8c45238953e82a%2Fpl_wall_-40378105',
                        'loaded_files/v2.mp4')

video = Video(
    url='', title='Как управлять своим состоянием и настроением',
    is_loaded=True, video_file_path='loaded_files/v2.mp4'
)
post = Post(
    url='https://vk.com/artursitapodcast?w=wall-40378105_82399',
    text='''🎙🎙🎙🎙🥰🥰😍😍😍😍Синица в руках или журавль в небе? Мечтать о чем-то великом или лучше быть удовлетворенным тем, что есть, и трезво оценивать свои возможности?
НОВЫЙ ВЫПУСК ПОДКАСТА на канале СКРЫТАЯ РЕАЛЬНОСТЬ, где Артур просто невероятно раскрыл эту тему и объяснил то, что навсегда изменит твой взгляд на этот выбор и вообще на то, как принимать ДЕЙСТВИТЕЛЬНО ПРАВИЛЬНЫЕ жизненные РЕШЕНИЯ 👍
Смотри этот подкаст и комментируй его под видео — пиши свои впечатления и открытия🤩 И конечно, делись этим подкастом с друзьями и близкими🥰''',
    videos=[video],
    photos=[]
)

ok = OK(
    group_id=cm.ok_group_id,
    access_token=cm.ok_access_token,
    app_key=cm.ok_app_key,
    app_secret=cm.ok_app_secret
)
ok.add_post(post)

