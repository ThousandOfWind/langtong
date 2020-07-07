import numpy as np
import torch as th
from .RL.dqn_learner import QLearner
from .RL.MF_learner_Counterparts import QLearner as MFLearner
from .RL.MF_learner_RNN import QLearner as MF_RNN
from .RL.epsilon_schedules import DecayThenFlatSchedule
class RL_Agents:
    def __init__(self, param_set, agent_id_list, writer, name):
        self.agent_id_list =agent_id_list
        self.batchSize = param_set['batch_size']
        self.learner = QLearner(param_set, writer=writer, name=name)
        self.schedule = DecayThenFlatSchedule(start=param_set['epsilon_start'], finish=param_set['epsilon_end'],
                                              time_length=param_set['time_length'], decay="linear")

        return

    def choose_action(self, obs, available_action, episode, std_out_type, memory, d_id, **arg):
        if np.random.rand()  < self.schedule.eval(episode):
            prop = available_action / available_action.sum()
            action = np.random.choice(range(len(available_action)), p=prop)
            if std_out_type['Q']:
                print('random', available_action, prop, action)
        else:
            device = th.device("cuda" if th.cuda.is_available() else "cpu")
            flag, lio = memory.get_current(d_id, 'immediately_obs')
            if not flag:
                lio = obs
            q = self.learner.approximate_Q(obs, lio).clone().squeeze()
            available_action = th.FloatTensor(available_action).to(device)
            q[available_action==0] = -9999
            action = q.argmax()
            if std_out_type['Q']:
                print('Q',q, action)
        return action

    def learn(self, memory, episode):
        """
        :param memory:
        :param episode:
        :return:
        """
        batch = memory.sample(self.agent_id_list, self.batchSize)
        self.learner.train(batch=batch, episode=episode)

class MF_Agents:
    def __init__(self, param_set, agent_id_list, writer, map, name):
        self.agent_id_list =agent_id_list
        self.batchSize = param_set['batch_size']
        self.learner = MFLearner(param_set, writer=writer, name=name)
        self.schedule = DecayThenFlatSchedule(start=param_set['epsilon_start'], finish=param_set['epsilon_end'],
                                              time_length=param_set['time_length'], decay="linear")
        self.map = map
        self.n_actions = param_set['n_actions']

        return

    def choose_action(self, obs, available_action, episode, std_out_type, memory, d_id, **arg):
        if np.random.rand()  < self.schedule.eval(episode):
            prop = available_action / available_action.sum()
            action = np.random.choice(range(len(available_action)), p=prop)
            if std_out_type['Q']:
                print('random', available_action, prop, action)
        else:
            device = th.device("cuda" if th.cuda.is_available() else "cpu")
            flag, lma = memory.get_current(d_id, 'last_mean_action', self.map)
            if not flag:
                lma = th.zeros(self.n_actions).to(device)
            flag, lio = memory.get_current(d_id, 'immediately_obs')
            if not flag:
                lio = obs
            q = self.learner.approximate_Q(obs, lma, lio).clone().squeeze()
            available_action = th.FloatTensor(available_action).to(device)
            q[available_action==0] = -9999
            action = q.argmax()
            if std_out_type['Q']:
                print('Q',q, action)
        return action

    def learn(self, memory, episode):
        """
        :param memory:
        :param episode:
        :return:
        """
        batch = memory.sample(self.agent_id_list, self.batchSize, mf=True, map=self.map)
        self.learner.train(batch=batch, episode=episode)

class MF_RNN_Agents:
    def __init__(self, param_set, agent_id_list, writer, map, name):
        self.agent_id_list =agent_id_list
        self.batchSize = param_set['batch_size']
        self.learner = MF_RNN(param_set, writer=writer, name=name)
        self.schedule = DecayThenFlatSchedule(start=param_set['epsilon_start'], finish=param_set['epsilon_end'],
                                              time_length=param_set['time_length'], decay="linear")
        self.map = map
        self.n_actions = param_set['n_actions']

        return

    def choose_action(self, obs, available_action, episode, std_out_type, memory, d_id, **arg):
        if np.random.rand()  < self.schedule.eval(episode):
            prop = available_action / available_action.sum()
            action = np.random.choice(range(len(available_action)), p=prop)
            if std_out_type['Q']:
                print('random', available_action, prop, action)
        else:
            device = th.device("cuda" if th.cuda.is_available() else "cpu")
            obs = th.FloatTensor(obs).to(device).reshape(1, -1).to(device)
            flag, batch = memory.get_current_trajectory(d_id, self.map)

            if flag:
                batch['obs'] = th.cat([batch['obs'], obs], dim=1)
            if not flag:
                batch = {
                    'bs':1,
                    'obs': obs,
                    'lio': obs,
                    'lma': th.zeros((1, self.n_actions)).to(device)
                }

            q = self.learner.approximate_Q(batch).clone().squeeze()
            available_action = th.FloatTensor(available_action).to(device)
            q[available_action==0] = -9999
            action = q.argmax()
            if std_out_type['Q']:
                print('Q',q, action)
        return action

    def learn(self, memory, episode):
        """
        :param memory:
        :param episode:
        :return:
        """
        batch = memory.sample(self.agent_id_list, self.batchSize, mf=True, map=self.map)
        self.learner.train(batch=batch, episode=episode)


class AM_Agents:
    def __init__(self, am):
        self.am = am
        return

    def choose_action(self, d_id, t, **arg):
        return self.get_action_from_art(d_id, t)

    def get_action_from_art(self, d_id, t):
        return self.am[d_id][t]

class Planner_Agents:
    def __init__(self, am):
        self.am = am
        return

    def choose_action(self, d_id, t, **arg):
        return self.get_action_from_art(d_id, t)

    def get_action_from_art(self, d_id, t):
        return self.am[d_id][t]


class Random_Agents:

    def choose_action(self, available_action, **arg):
        prop = available_action/ available_action.sum()
        action = np.random.choice(range(len(available_action)), p=prop)
        return action

    def learn(self, **arg):
        return



def init_Agents(param_set, agent_id_list=None, writer=None, map=None, name=None):
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
        return RL_Agents(param_set, agent_id_list, writer, name)
    if agentType == 'MF':
        return MF_Agents(param_set, agent_id_list, writer, map, name)
    if agentType == 'MF-RNN':
        return MF_Agents(param_set, agent_id_list, writer, map, name)
    return