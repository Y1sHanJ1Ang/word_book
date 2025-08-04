import requests
import json
from typing import Dict, Optional

class DictionaryAPI:
    def __init__(self):
        self.youdao_url = "https://dict.youdao.com/suggest"
        self.fallback_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
    
    def query_word(self, word: str) -> Dict[str, str]:
        result = {
            'word': word,
            'translation': '',
            'english_translation': '',
            'memory_tip': ''
        }
        
        translation = self._query_youdao(word)
        if translation:
            result['translation'] = translation
        
        english_def = self._query_english_dict(word)
        if english_def:
            result['english_translation'] = english_def
        
        return result
    
    def _query_youdao(self, word: str) -> Optional[str]:
        try:
            params = {
                'q': word,
                'doctype': 'json'
            }
            response = requests.get(self.youdao_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'entries' in data['data']:
                    entries = data['data']['entries']
                    if entries:
                        return entries[0].get('explain', '')
        except Exception as e:
            print(f"有道API查询失败: {e}")
        
        return None
    
    def _query_english_dict(self, word: str) -> Optional[str]:
        try:
            url = f"{self.fallback_url}{word}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    meanings = data[0].get('meanings', [])
                    if meanings:
                        definitions = meanings[0].get('definitions', [])
                        if definitions:
                            return definitions[0].get('definition', '')
        except Exception as e:
            print(f"英文词典API查询失败: {e}")
        
        return None
    
    def generate_memory_tip(self, word: str, translation: str) -> str:
        tips = [
            f"联想记忆: {word} → {translation}",
            f"词根记忆: 分析 {word} 的构成",
            f"发音记忆: {word} 的发音特点",
            f"造句记忆: 用 {word} 造个句子"
        ]
        return tips[0]