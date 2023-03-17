import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.webdriver import WebDriver as EdgeWebDriver
import traceback


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


class BaiduFanyi:
    EDGE_BROWSER: EdgeWebDriver
    URL = 'https://fanyi.baidu.com/#en/zh/{word}'

    def __init__(self, word) -> None:
        if not hasattr(BaiduFanyi, "EDGE_BROWSER"):
            edge_options = Options()
            edge_options.add_argument('--headless')
            edge_options.add_argument('--disable-gpu')
            edge_browser = webdriver.Edge(
                service=Service("driver/msedgedriver.exe"),
                options=edge_options
            )
            BaiduFanyi.EDGE_BROWSER = edge_browser
        self.edge_browser = BaiduFanyi.EDGE_BROWSER
        self.if_definitions_found = False
        self._get_phonetic(word)
        if self.if_definitions_found:
            self._get_definition()

    def _get_definition(self):
        definitions = [i.text for i in self.edge_browser.find_elements('xpath', r"//div[@class='dictionary-comment']/*")]
        definitions = [i.strip().replace('\n', ' ').replace(';', '，') for i in definitions]
        self.definitions = "\n".join(definitions)

    def _get_phonetic(self, word):
        def format_phonetic(p):
            if p[0] != '[':
                p = '['+p
            if p[-1] != ']':
                p = p+']'
            return p

        def parse_page():
            types = [i.text for i in self.edge_browser.find_elements('xpath', r"//label[@class='op-sound-wrap']/span")]
            types = [i.replace(r'/', '').strip() for i in types]
            phonetics = [i.text for i in self.edge_browser.find_elements('xpath', r"//label[@class='op-sound-wrap']/b")]
            phonetics = [format_phonetic(i) for i in phonetics]
            return list(zip(types, phonetics))

        def check_finish_loading(word):
            dictionary_title_obj = self.edge_browser.find_elements('xpath', r"//div[@class='dictionary-title']/h3[@class='strong']")
            if len(dictionary_title_obj) > 0:
                dictionary_title = dictionary_title_obj[0].text
                if dictionary_title == word:
                    return True
                else:
                    return False
            else:
                return False

        try:
            self.edge_browser.get(BaiduFanyi.URL.format(word=word))
            phonetics_info = []
            for _ in range(60):
                phonetics_info = parse_page()
                if (not check_finish_loading(word)) or (len(phonetics_info) == 0):
                    time.sleep(1)
                else:
                    break
            if len(phonetics_info) > 0:
                self.phonetic_string = "   ".join([f"{i[0]}{i[-1]}" for i in phonetics_info])
                self.if_definitions_found = True
        except:
            traceback.print_exc()
