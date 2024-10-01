import random
from constants import INITIAL_FIRST_LEVEL_COMMISSION_PERCENT, INITIAL_POS_PROBABILITY_PERCENT, INITIAL_GRAVITY_COMMISSION_PERCENT

def get_commission_percent_by_distant(d):
    return INITIAL_FIRST_LEVEL_COMMISSION_PERCENT / (2 ** (d - 1))

def get_prob_backward_pos_of_user(user):
    return INITIAL_POS_PROBABILITY_PERCENT / 100  # 10% for now

def get_prob_backward_pow_by_distant(d):
    if d == 1:
        return 0.99  # 99%
    elif d == 2:
        return 0.90  # 90%
    elif d == 3:
        return 0.50  # 50%
    elif d == 4:
        return 0.10  # 10%
    else:  # For d > 4
        return 0.10 - (0.01 * (d - 4))  # Decrease by 1% per distant beyond 4, allowing probabilities to become negative.

def compute_probability(pow: float, pos: float) -> bool:
    probability = pow + pos
    return random.random() < probability     

def compute_commission(benefit, percent_commission, pow, pos):
    result = 0

    if not compute_probability(pow=pow, pos=pos):
        return result

    result = benefit * percent_commission / 100
    return result       

def gravity_probability(node) -> float:
    if node.parent is None:
        return 1.0  # Root node should return 100% probability or some default
    return node.size / node.parent.size
