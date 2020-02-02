from datetime import datetime


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
    res = int(text[:2]) * 3600
    res += int(text[3:5]) * 60
    res += int(text[6:8])

    return res
