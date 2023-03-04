import json
import requests


class FreeDictionary:
    API = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    def __init__(self, word) -> None:
        self.if_definitions_found = False
        self._get_definitions(word)
        if self.if_definitions_found:
            self._get_phonetic()

    def _get_definitions(self, word):
        try:
            response = requests.get(FreeDictionary.API.format(word=word))
            response.raise_for_status()
            result = json.loads(response.content)
            if isinstance(result, list) and len(result) > 0:
                self.if_definitions_found = True
                self.result = result
        except:
            pass

    def _get_phonetic(self):
        def format(p):
            return p.replace(r'/', r'[', 1).replace(r'/', r']', 1)

        phonetics = set()
        for word_info in self.result:
            p = word_info.get('phonetic')
            if p:
                phonetics.add(format(p))
            ps = word_info.get('phonetics')
            if ps:
                for p in ps:
                    t = p.get('text')
                    if t:
                        phonetics.add(format(t))
        self.phonetic_string = " ".join(phonetics)
