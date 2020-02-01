import os
import requests
import json
from bs4 import BeautifulSoup
from logger import logger
from datetime import datetime
import random
import time

from html_anchors import (
    PLAYER_NAME_CLASS,
    GAME_FINISHED_CLASS,
    GAME_DURATION_CLASS,
    TOTAL_POINTS_CLASS
)
from urls import(
    URL_GAME_REPLAY,
    URL_GAME_INFO
)

PROJ_FOLDER = os.path.dirname(os.path.abspath(__file__))
LOGGER = logger('get_data')
HEADERS = {'User-Agent': 'Mozilla/5.0'}
with open(PROJ_FOLDER + '/assets/config.json', 'r') as f:
    CONFIG = json.load(f)


def get_html_content(url: str, id: int, session) -> str:
    # returns html text form given url, game id and session
    res = session.get(
        f'{url}?id={id}',
        headers=HEADERS

    )

    return res.text


def get_game_replay_data(text: str) -> dict:
    # returns replay related game data like
    # moves and scores
    tag = 'parseJSON'
    labels = ('game', 'score')
    data = {}
    ix_from, ix_to = 0, 0

    for i in range(2):
        ix_from = text.find(tag, ix_from + 1)
        if ix_from < 0:
            return data
        ix_to = text.find(");", ix_from)
        json_text = text[ix_from: ix_to]
        json_text = json_text[len(tag) + 2: -1]
        data[labels[i]] = json.loads(json_text)

    return data


def get_game_info_data(text: str) -> dict:
    # returns info related game data like
    # game date, duration and points
    data = {}

    # getting game date
    bs = BeautifulSoup(text, "html.parser")
    tags = bs.find_all(attrs={'class': GAME_FINISHED_CLASS})
    data['game_date'] = tags[0].find('b').getText()
    # getting game winner
    winner_text = tags[1].getText().replace('\n', '')
    # winner = winner[25:]
    # winner = winner[:winner.find(' după ')]
    data['winner_text'] = winner_text

    # getting game duration
    tags = bs.find_all(attrs={'class': GAME_DURATION_CLASS})
    data['game_duration'] = tags[0].find('b').getText()

    # getting player names
    names = []
    tags = bs.find_all(attrs={'class': PLAYER_NAME_CLASS})
    for tag in tags[1:]:  # first one is logged in user
        names.append(tag.getText())
    data['players'] = names

    # get all players points
    points = []
    tags = bs.find_all(attrs={'class': TOTAL_POINTS_CLASS})
    for tag in tags:  # first one is logged in user
        points.append(tag.getText())
    points = [point.split()[0] for point in points]
    data['points'] = points

    return data


def get_game_data(id: int) -> dict:
    # returns information for game with id=id
    session = get_session()

    # getting data form game replay page
    html_content = get_html_content(
        URL_GAME_REPLAY,
        id,
        session
    )

    data = {}

    # getting score and moves from game replay
    data.update(get_game_replay_data(html_content))

    # getting data from game info page
    html_content = get_html_content(
        URL_GAME_INFO,
        id,
        session
    )

    data.update(get_game_info_data(html_content))

    # setting datetime when data was obtained
    # data['date_crawled'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return data


def get_session(config: dict = CONFIG):
    # returns a request session object
    payload = {'action': 'login'}
    payload['login'] = config.get('login', '')
    payload['pass'] = config.get('pass', '')

    session = requests.Session()
    session.post(
        'https://belot.md/action.php',
        headers=HEADERS,
        data=payload
    )

    return session


if __name__ == "__main__":
    id = 16080002
    ress = []
    for i in range(id, id + 15):
        ress.append(get_game_data(i))
        time.sleep(random.randint(100, 300) / 100)
    with open('data/result.json', 'w') as fp:
        json.dump(ress, fp)
