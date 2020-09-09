"""
定义损失/奖赏
"""

BASE_REWARD_RUlE = {
    'step': 0,
    'meet_need': 0,
    'wait': -0.01,
    'changeCraft': -1,
    'success': 100,
    'reduce_time': 10,
    'fail': -1000,
    'fail-order': -10,
    'remain-order': 0,
    'exceed-time': 0
}

STEP_REWARD_RUlE = {
    'step': -0.01,
    'meet_need': 0,
    'wait': 0,
    'changeCraft': 0,
    'success': 0,
    'reduce_time': 0,
    'fail': 0,
    'fail-order': 0,
    'remain-order': 0,
    'exceed-time': 0
}

PUNISH_REWARD_RUlE = {
    'step': 0,
    'meet_need': 0,
    'wait': -0.01,
    'changeCraft': -1,
    'success': 0,
    'reduce_time': 0,
    'fail': -100,
    'fail-order': -1,
    'exceed-time': 0,
    'remain-order': 0,
}


MNP_REWARD_RUlE = {
    'step': 0,
    'meet_need': 1,
    'wait': -0.01,
    'changeCraft': -1,
    'success': 0,
    'reduce_time': 0,
    'fail': -100,
    'fail-order': -1,
    'exceed-time': 0,
    'remain-order': 0,
}

MIX_REWARD_RUlE = {
    'step': -0.1,
    'meet_need': 1,
    'wait': -0.01,
    'changeCraft': -1,
    'success': 0,
    'reduce_time': 0,
    'fail': -100,
    'fail-order': -1,
    'exceed-time': 0,
    'remain-order': 0,
}

SE_REWARD_RUlE = {
    'step': -0.1,
    'meet_need': 0.1,
    'wait': 0,
    'changeCraft': 0,
    'success': 0,
    'reduce_time': 0,
    'fail': 0,
    'fail-order': 0,
    'remain-order': 0,
    'exceed-time': 0
}


POSITIVE_REWARD_RUlE = {
    'step': 0,
    'meet_need': 1,
    'wait': 0,
    'changeCraft': 0,
    'success': 1000,
    'reduce_time': 0,
    'fail': 0,
    'fail-order': 0,
    'remain-order': 0,
    'exceed-time': 0
}

SE2_REWARD_RUlE = {
    'step': -0.2,
    'meet_need': 0.1,
    'wait': 0,
    'changeCraft': 0,
    'success': 0,
    'reduce_time': 0,
    'fail': 0,
    'fail-order': 0,
    'remain-order': 0,
    'exceed-time': 0
}

PC_REWARD_RUlE = {
    'step': -0.2,
    'meet_need': 0,
    'wait': 0,
    'changeCraft': -0.01,
    'success': 0,
    'reduce_time': 0,
    'fail': 0,
    'fail-order': 0,
    'remain-order': 0,
    'exceed-time': 0
}



REWARD_RUlE = {
    'base': BASE_REWARD_RUlE,
    'step': STEP_REWARD_RUlE,
    'punish': PUNISH_REWARD_RUlE,
    'mnp': MNP_REWARD_RUlE,
    'mix': MIX_REWARD_RUlE,
    'se': SE_REWARD_RUlE,
    'se2': SE2_REWARD_RUlE,
    'positive': POSITIVE_REWARD_RUlE,
    'pc': PC_REWARD_RUlE,
}

