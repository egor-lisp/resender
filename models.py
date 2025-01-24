class Video:
    def __init__(self, url, title, is_loaded=False, video_file_path=None, size=None):
        self.url = url
        self.title = title
        self.is_loaded_local = is_loaded
        self.file_path = video_file_path
        self.file_size = size


class Photo:
    def __init__(self, url, is_loaded=False, photo_file_path=None):
        self.url = url
        self.is_loaded_local = is_loaded
        self.file_path = photo_file_path


class Post:
    def __init__(self, url, text, photos: list[Photo], videos: list[Video]):
        self.url = url
        self.text = text
        self.photos = photos
        self.videos = videos
