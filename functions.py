from constants import INITIAL_COMMISSION_PERCENT, ADDITIONAL_POS_PROBABILITY_PERCENT

def get_commission_percent_by_distant(d):
    return INITIAL_COMMISSION_PERCENT / (2 ** (d - 1))

def get_prob_backward_pos_of_user(user):
    return ADDITIONAL_POS_PROBABILITY_PERCENT / 100  # 10% for now

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
