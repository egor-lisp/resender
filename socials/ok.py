from ok_api import OkApi, Upload
from models import Post
import json


class OK:

    def __init__(self, group_id, access_token, app_key, app_secret):
        self.ok = OkApi(access_token=access_token,
                        application_key=app_key,
                        application_secret_key=app_secret)
        self.upload = Upload(self.ok)
        self.group_id = group_id

    def upload_photos(self, photo_paths: list):
        upload_response = self.upload.photo(photos=photo_paths, group_id=self.group_id)
        uploaded_photo_ids = []

        for photo_id in upload_response['photos']:
            token = upload_response['photos'][photo_id]['token']
            response = self.ok.photosV2.commit(photo_id=photo_id, token=token)
            data = response.json()
            if data['photos'][0]['status'] != 'SUCCESS':
                print(f'Ошибка в коммите фото {photo_id}')
                continue
            uploaded_photo_ids.append({"id": token})
        return uploaded_photo_ids

    def upload_video(self, file_path, title):
        upload_response = self.upload.video(video=file_path, file_name=file_path)
        response = self.ok.video.update(vid=upload_response['video_id'], title=title)
        if response.text == "":
            return upload_response['video_id']

    def add_post(self, post: Post):
        attachment = {'media': []}
        if post.text:
            attachment['media'].append({'type': 'text', 'text': post.text})

        if post.photos:
            photos_paths = [photo.file_path for photo in post.photos]
            uploaded_photo_ids = self.upload_photos(photos_paths)
            if uploaded_photo_ids:
                attachment['media'].append({'type': 'photo', 'list': uploaded_photo_ids})

        if post.videos:
            videos_ids = []
            for video in post.videos:
                video_id = self.upload_video(video.file_path, video.title)
                if video_id:
                    videos_ids.append({'id': video_id})
            if videos_ids:
                attachment['media'].append({'type': 'movie', 'list': videos_ids})

        attachment = json.dumps(attachment)

        res = self.ok.mediatopic.post(
            type='GROUP_THEME', gid=self.group_id, attachment=attachment,
        )
        return res
