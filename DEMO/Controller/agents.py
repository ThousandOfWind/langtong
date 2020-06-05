import numpy as np
import torch as th
from .RL.dqn_learner import QLearner
from .RL.epsilon_schedules import DecayThenFlatSchedule
class RL_Agents:
    def __init__(self, param_set, agent_id_list, writer):
        self.agent_id_list =agent_id_list
        self.batchSize = param_set['batch_size']
        self.learner = QLearner(param_set, writer=writer)
        self.schedule = DecayThenFlatSchedule(start=param_set['epsilon_start'], finish=param_set['epsilon_end'],
                                              time_length=param_set['time_length'], decay="linear")

        return

    def choose_action(self, state, available_action, episode):
        if np.random.rand()  < self.schedule.eval(episode):
            prop = available_action / available_action.sum()
            action = np.random.choice(range(len(available_action)), p=prop)
        else:
            q = self.learner.approximate_Q(state).clone()
            q[available_action == 0] = -9999
            action = q.argmax(dim=1)
        return action

    def learn(self, memory, episode):
        """
        :param memory:
        :param episode:
        :return:
        """
        batch = memory.sample(self.agent_id_list, self.batchSize)
        self.learner.train(batch=batch, episode=episode)


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



def init_Agents(param_set, agent_id_list=None, writer=None):
    """
    :param stage_info:
    :return:  [Agents] / Agents
    """
    agentType = param_set['agentType']
    if agentType=='random':
        return Random_Agents()
    if agentType=='AM':
        return AM_Agents(param_set)
    if agentType == 'RL':
        return RL_Agents(param_set, agent_id_list, writer)
    return