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
    TOTAL_POINTS_CLASS,
    FOUR_PLAYERS_CLASS
)
from urls import(
    URL_GAME_REPLAY,
    URL_GAME_INFO
)

PROJ_FOLDER = os.path.dirname(os.path.abspath(__file__))
LOGGER = logger('crawler')
HEADERS = {'User-Agent': 'Mozilla/5.0'}
CONFIG_PATH = PROJ_FOLDER + '/assets/config.json'
with open(CONFIG_PATH, 'r') as f:
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
    if len(names) == 4:  # special case when there are 4 players
        tags = bs.find_all(attrs={'class': FOUR_PLAYERS_CLASS})
        for tag in tags:
            inner_tags = tag.find_all('b')
            for inner_tag in inner_tags:
                points.append(inner_tag.getText())

    else:
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

    data = {'id': id}

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


def save_batch_data(data):
    id_start = data[0]['id']
    id_end = data[-1]['id']
    filename = f"{PROJ_FOLDER}/data/{id_start}_{id_end}.json"
    with open(filename, 'w') as f:
        json.dump(data, f)
    LOGGER.info(f'saved data in {filename}')


def update_config(data):
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    config.update(data)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)


def crawl_batch(id_start: int, batch_size: int = 5) -> bool:
    # runs crawler for ids between from id_start to + batch_size
    # returns False if no data is crawled, True otherwise
    LOGGER.info(f"crawler batch for {id_start} started")
    data = []
    for i in range(id_start, id_start + batch_size):
        data.append(get_game_data(i))
        # a very lame imitation of user behavior
        # trying to be "polite" to server actually
        time.sleep(random.randint(100, 300) / 100)

    # safe check
    if len(data) == 0 or 'players' not in data[0]:
        LOGGER.info(f'No data received in crawl_batch for id = {id_start}')
        return False

    # saving data
    save_batch_data(data)

    # updating last processed game id in config file

    update_data = {"last_processed_game_id": data[-1]['id']}
    update_config(update_data)

    return True


def run_crawler(n_iterations: int, batch_size: int = 1000):
    # runs crawl_batch n_iterations times
    ix = CONFIG['last_processed_game_id']
    LOGGER.info(f'starting crawler with id_start = {ix}')
    for _ in range(n_iterations):
        crawl_batch(ix, batch_size=batch_size)
        ix += batch_size
        # sleeping for 3-5 seconds, trying to be polite
        time.sleep(random.randint(300, 500) / 100)

    LOGGER.info('crawler successfully finished')


if __name__ == "__main__":
    run_crawler(2, batch_size=10)
