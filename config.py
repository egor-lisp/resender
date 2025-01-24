import json


class ConfigManager:
    config_path = 'config.json'

    vk_token: str
    vk_group_id: str

    ok_access_token: str
    ok_app_key: str
    ok_app_secret: str
    ok_group_id: str

    tg_bot_token: str
    tg_admin_ids: list

    ok_resend: bool

    def __init__(self):
        self.read_config()
        # Описание переменных в конфиге
        self.config_vars_description = {
            self.vk_token: {'desc': 'Введите токен группы ВК:', 'name': 'vk_token'},
            self.vk_group_id: {'desc': 'Введите ID группы ВК:', 'name': 'vk_group_id'},
            self.ok_access_token: {'desc': 'Введите Access Token от одноклассников:', 'name': 'ok_access_token'},
            self.ok_app_key: {'desc': 'Введите Application key от ОК:', 'name': 'ok_app_key'},
            self.ok_app_secret: {'desc': 'Введите Application secret от ОК:', 'name': 'ok_app_secret'},
            self.ok_group_id: {'desc': 'Введите ID группы в ОК:', 'name': 'ok_group_id'}
        }
        self.settings_must_setup = []

    def read_config(self):
        with open(self.config_path, 'r') as f:
            data = json.load(f)

        self.vk_token = data.get('vk_token')
        self.vk_group_id = data.get('vk_group_id')

        self.ok_access_token = data.get('ok_access_token')
        self.ok_app_key = data.get('ok_app_key')
        self.ok_app_secret = data.get('ok_app_secret')
        self.ok_group_id = data.get('ok_group_id')

        self.tg_bot_token = data.get('tg_bot_token')
        self.tg_admin_ids = data.get('tg_admin_ids', [])

        self.ok_resend = data.get('ok_resend', False)

    def save_config(self):
        data = {
            'vk_token': self.vk_token,
            'vk_group_id': self.vk_group_id,
            'ok_access_token': self.ok_access_token,
            'ok_app_key': self.ok_app_key,
            'ok_app_secret': self.ok_app_secret,
            'ok_group_id': self.ok_group_id,
            'tg_bot_token': self.tg_bot_token,
            'tg_admin_ids': self.tg_admin_ids,
            'ok_resend': self.ok_resend
        }
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=3)
