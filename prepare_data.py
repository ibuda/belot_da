from datetime import datetime

game_categories = {
    'Jucatorul ': 0,
    'Jocul a fost castigat de': 1,
    'Razboi intre clanuri, ': 2,
    'Campionat etapa: ': 3,
    'Liga ': 4,
}


def parse_game_date(text: str) -> datetime:
    # parsing custom data string to datetime
    text = text.replace('Noi.', '11')
    text = text.replace('Dec.', '12')
    text = text.replace('Ian.', '01')
    text = text.replace('Feb.', '02')
    text = text.replace(', Ora ', ' ')
    dt = datetime.strptime(text, '%d %m %Y %H:%M:%S')

    return dt


def parse_game_duration(text: str) -> int:
    # returns game duration in seconds
    if text is None or text == '':
        return 0
    res = int(text[:2]) * 3600
    res += int(text[3:5]) * 60
    res += int(text[6:8])

    return res


def parse_winner_text(text: str):
    for key, val in game_categories.items():
        if text.startswith(key):
            return val

    return -1


def parse_winners(text: str, game_type: int):
    # getting winner player name
    if game_type == 0:
        text = text[10:]
        return text[: text.find(' ')]
    elif game_type == 1:
        text = text[25:]
        return text[: text.find(' ')]
