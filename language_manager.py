import json
import os

class LanguageManager:
    def __init__(self, default_language='en'):
        self.default_language = default_language
        self.languages = {}
        self.load_languages()

    def load_languages(self):
        for filename in os.listdir('locales'):
            if filename.endswith('.json'):
                lang_code = filename[:-5]
                with open(f'locales/{filename}', 'r', encoding='utf-8') as file:
                    self.languages[lang_code] = json.load(file)

    def get_text(self, key, lang_code=None):
        lang_code = lang_code or self.default_language
        return self.languages.get(lang_code, {}).get(key, self.languages[self.default_language].get(key, key))

lang_manager = LanguageManager()