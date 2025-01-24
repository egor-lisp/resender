import requests
import random
import string
import re


def load_photo_by_url(url, file_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # Открытие файла для записи в бинарном режиме
        with open(file_path, 'wb') as file:
            # Запись содержимого изображения по частям
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f'Изображение успешно загружено и сохранено как {file_path}')
        return True
    else:
        print(f'Не удалось загрузить изображение: код ответа {response.status_code}')


def download_vk_video(url, file_path):
    """ Используем сервис https://ru.get-save.com/"""
    """ Ссылка на видео типа https://vk.com/video-204324233_456239017 """
    headers = {
        'accept': 'application/json',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://ru.get-save.com',
        'priority': 'u=1, i',
        'referer': 'https://ru.get-save.com/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    json_data = {'url': url}
    res = requests.post('https://api.get-save.com/api/v1/vidinfo', headers=headers, json=json_data)
    data = res.json()
    sizes = data['sizes']

    filtered_videos = list(filter(
        lambda size: size['protocol'] == 'https' and size['ext'] == 'mp4', sizes)
    )

    if filtered_videos:
        max_resolution_elem = max(
            filtered_videos,
            key=lambda size: size.get('height', 0)
        )
        download_url = max_resolution_elem['url']
        headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'If-Modified-Since': 'Wed, 1 Jan 2014 00:00:00 GMT',
                'Range': 'bytes=0-1048575',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }
        response = requests.get(download_url, headers=headers, stream=True)
        if response.status_code in [200, 206]:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f'Видео успешно загружено и сохранено как {file_path}')
            return True
        else:
            print(f'Не удалось загрузить видео: код ответа {response.status_code}')


def replace_allias_vk_urls(text: str):
    pattern = r'\[#alias\|[^|]+\|[^|]+\]'
    matches = re.findall(pattern, text)
    for match in matches:
        url = match.split('|')[-1].split(']')[0]
        text = text.replace(match, url)
    return text


def random_string(length):
    characters = string.ascii_letters + string.digits
    random_str = ''.join(random.choice(characters) for _ in range(length))
    return random_str
