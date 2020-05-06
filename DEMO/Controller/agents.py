import numpy as np

class RL_Agents:
    def __init__(self, stage_info):
        return


class AM_Agents:
    def __init__(self, am):
        self.am = am
        return

    def choose_action(self, id, t, **arg):
        return self.get_action_from_art(id, t)

    def get_action_from_art(self, id, t):
        return self.am[id][t]


class Random_Agents:

    def choose_action(self, available_action, **arg):
        prop = available_action/ available_action.sum()
        action = np.random.choice(range(len(available_action)), p=prop)
        return action

    def learn(self, **arg):
        return



def init_Agents(stage_info, memory=None ,agentType='random', am=None):
    """
    :param stage_info:
    :return:  [Agents]
    """
    if agentType=='random':
        return Random_Agents()
    if agentType=='AM':
        if am:
            return AM_Agents(am)
        else:
            '没有加载调度'
    if agentType == 'RL':
        return RL_Agents(stage_info)
    return