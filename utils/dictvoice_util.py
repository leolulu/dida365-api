import requests
import io
from enum import Enum, unique


@unique
class VoiceType(Enum):
    UK = 1
    US = 0


def request_dictvoice(type, word):
    url = "http://dict.youdao.com/dictvoice?type={type}&audio={word}"
    r = requests.get(url.format(type=type, word=word))
    r.raise_for_status()
    return r.content


def get_dictvoice_bytes(word):
    result = []
    for type_name, type_value in VoiceType.__members__.items():
        type_value = type_value.value
        r_content = request_dictvoice(type_value, word)
        result.append((type_name, io.BytesIO(r_content)))
    return result
