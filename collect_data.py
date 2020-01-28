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


def get_game_data():
    payload = {'action': 'login'}
    payload['login'] = CONFIG.get('login', '')
    payload['pass'] = CONFIG.get('pass', '')

    session = requests.Session()
    session.post(
        'https://belot.md/action.php',
        headers=HEADERS,
        data=payload
    )

    html_content = get_game_html(16020000, session)

    bs = BeautifulSoup(html_content, "html.parser")

    # getting player names
    html_names = bs.find_all(attrs={'style': PLAYER_NAME_STYLE})
    names = []
    for html_name in html_names:
        names.append(html_name.renderContents().decode("utf-8"))

    return names


if __name__ == "__main__":
    res = get_game_data()
    # print('data = $.parseJSON' in res.text)
    print(res)
    # print(res.response)
