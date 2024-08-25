from typing import List


def parse_market_probability_string(market_probability: str) -> List[float]:
    prob_list = market_probability.split(sep='/')
    # prepare probabilities for numpy: 10 -> 0.1
    prob_list = [int(item) / 100 for item in prob_list]
    return prob_list


def convert_market_probability_string(bes: int, be: int, id: int, bu: int, bus: int) -> str:
    pass


def convert_market_probability_string(prob_list: List[int]) -> str:
    # to bring [0.1, 0.2,..] in form "10/20/..."
    prob_list = [str(int(num * 100)) for num in prob_list]
    market_probability_string = "/".join(prob_list)
    return market_probability_string


def rearrange_market_probabilities(prob_list: List[float], market_mode: str) -> List[float]:
    if market_mode == "BES":
        diff = round((prob_list[0]), 2)
        prob_list[0] = round((prob_list[0] - diff), 2)
        # prob_list[2] = round((prob_list[2] + diff / 2), 2)
        prob_list[3] = round((prob_list[3] + diff), 2)
    if market_mode == "BE":
        diff = round((prob_list[1] / 2), 2)
        prob_list[1] = round((prob_list[1] - diff), 2)
        prob_list[3] = round((prob_list[3] + diff), 2)
    if market_mode == "ID":
        diff = round((prob_list[2] / 2), 2)
        prob_list[2] = round((prob_list[2] - diff), 2)
        prob_list[1] = round((prob_list[1] + diff / 4), 2)
        prob_list[3] = round((prob_list[3] + diff / 2), 2)
        prob_list[4] = round((prob_list[4] + diff / 4), 2)
    if market_mode == "BU":
        diff = round((prob_list[3] / 16), 2)
        prob_list[3] = round((prob_list[3] - diff), 2)
        prob_list[1] = round((prob_list[1] + diff / 4), 2)
        prob_list[2] = round((prob_list[2] + diff / 2), 2)
        prob_list[4] = round((prob_list[4] + diff / 4), 2)
    if market_mode == "BUS":
        diff = round((prob_list[4] / 2), 2)
        prob_list[4] = round((prob_list[4] - diff), 2)
        prob_list[2] = round((prob_list[2] + diff / 2), 2)
        prob_list[3] = round((prob_list[3] + diff / 2), 2)

    s = sum(prob_list)
    if s != 1:
        diff = round(1 - s, 2)
        prob_list[3] = prob_list[3] + diff

    return prob_list


# Abbildung von [0, max_value] -> [-1, 1]
def moral_percentage(invested: int, max_value: int) -> float:
    # Clamp [0 <= invested <= max_value]
    invested = 0 if invested < 0 else max_value if invested > max_value else invested
    # Scale & Translate [0, max_value] -> [0, 2] -> [-1, 1]
    return float(invested) / float(max_value) * 2.0 - 1.0 
