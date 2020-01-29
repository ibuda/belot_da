import requests
import json
from bs4 import BeautifulSoup
from logger import logger


from anchors import (
    PLAYER_NAME_STYLE
)

LOGGER = logger('get_data')
HEADERS = {'User-Agent': 'Mozilla/5.0'}
with open('assets/config.json', 'r') as f:
    CONFIG = json.load(f)


def get_game_html(id, session):
    res = session.get(
        f'https://belot.md/replay.php?id={id}',
        headers=HEADERS

    )
    return res.text


def get_game_json_data(text):
    tag = 'parseJSON'
    labels = ('game', 'score')
    ix_from, ix_to = 0, 0
    data = {}
    for i in range(2):
        ix_from = text.find(tag, ix_from + 1)
        ix_to = text.find(");", ix_from)
        json_text = text[ix_from: ix_to]
        json_text = json_text[len(tag) + 2: -1]
        data[labels[i]] = json.loads(json_text)

    return data


def get_game_data(id: int):
    payload = {'action': 'login'}
    payload['login'] = CONFIG.get('login', '')
    payload['pass'] = CONFIG.get('pass', '')

    session = requests.Session()
    session.post(
        'https://belot.md/action.php',
        headers=HEADERS,
        data=payload
    )

    html_content = get_game_html(id, session)

    bs = BeautifulSoup(html_content, "html.parser")

    data = {}
    data['id'] = id
    # getting player names
    html_names = bs.find_all(attrs={'style': PLAYER_NAME_STYLE})
    names = []
    for html_name in html_names:
        names.append(html_name.renderContents().decode("utf-8"))

    data['players'] = names

    # getting game data
    data.update(get_game_json_data(html_content))

    return data


if __name__ == "__main__":
    res = get_game_data(16030000)
    # print('data = $.parseJSON' in res.text)
    print(res)
    print('id' in res)
    # print(res.response)
