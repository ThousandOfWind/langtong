import copy
import torch as th
from torch.optim import Adam
import numpy as np
import random as rd

import os

from Controller.RL.NN import NN

class QLearner:
    """
    1. DQN- RNNAgent
    2. train
    """
    def __init__(self,param_set, writer, name):
        self.obs_shape = param_set['obs_shape']
        self.gamma = param_set['gamma']
        self.learning_rate = param_set['learning_rate']
        self.grad_norm_clip = param_set['grad_norm_clip']

        self.ob_style = param_set['ob_style']
        self.Q = NN['MF-RNN'](param_set)

        self.params = self.Q.parameters()
        self.target_Q = copy.deepcopy(self.Q)

        if param_set['cuda']:
            self.Q.cuda()
            self.target_Q.cuda()

        self.optimiser = Adam(params=self.params, lr=self.learning_rate)
        self.train_step = 0
        self.last_update_step = 0
        self.update_frequncy = param_set['target_update_interval']
        self.writer = writer
        self.name = name

    def update(self):
        self.target_Q.load_state_dict(self.Q.state_dict())

    def approximate_Q(self, batch):
        hidden_states = self.Q.init_hidden()
        for t in range(len(batch['obs'])):
            q, hidden_states = self.Q(obs=batch['obs'][t:t+1], action_prob=batch['lma'][t:t+1], hidden_state=hidden_states)
        return q



    def train(self, batch, episode):

        self.train_step += 1

        hidden_states = self.Q.init_hidden().unsqueeze(0).expand(batch['bs'], -1)
        q_batch = []
        for t, done in enumerate(batch['done'][0]):
            q, hidden_states = self.Q(obs=batch['obs'][:, t], action_prob=batch['lma'][:, t], hidden_state=hidden_states)
            q_batch.append(q)
            if done:
                hidden_states = self.Q.init_hidden().unsqueeze(0).expand(batch['bs'], -1)
        q_batch = th.stack(q_batch, dim=1)

        next_hidden_states = self.target_Q.init_hidden().unsqueeze(0).expand(batch['bs'], -1)
        next_q_batch = []
        _, next_hidden_states = self.target_Q(obs=batch['obs'][:,0], action_prob=batch['lma'][:,0], hidden_state=next_hidden_states)
        for t, done in enumerate(batch['done'][0]):
            q, next_hidden_states = self.target_Q(obs=batch['obs'][:, t], action_prob=batch['lma'][:, t], hidden_state=next_hidden_states)
            next_q_batch.append(q)
            if done:
                if t == len(batch['done'][0]) -1:
                    break
                next_hidden_states = self.target_Q.init_hidden().unsqueeze(0).expand(batch['bs'], -1)
                _, next_hidden_states = self.target_Q(obs=batch['obs'][:, t+1], action_prob=batch['lma'][:,t+1],
                                                      hidden_state=next_hidden_states)
        next_q_batch = th.stack(next_q_batch, dim=1)

        chosen_action_qvals = th.gather(q, dim=2, index=batch['action'].unsqueeze(-1)).squeeze(-1)


        next_q_batch[batch['next_avail_action'] == 0] = -9999
        next_max_q, _ = next_q_batch.max(dim=1)

        targets = (batch['reward'] + self.gamma * (1 - batch['done']) * next_max_q).detach()
        loss = ((chosen_action_qvals - targets) ** 2).sum()

        self.writer.add_scalar('Loss/TD_loss_'+self.name, loss.item(), episode)

        # Optimise
        self.optimiser.zero_grad()
        loss.backward()
        grad_norm = th.nn.utils.clip_grad_norm_(self.params, self.grad_norm_clip)
        self.optimiser.step()

        # if (loss) < 0.25 and (self.train_step - self.last_update_step)/self.update_frequncy >= 1.0:
        if (self.train_step - self.last_update_step)/self.update_frequncy >= 1.0:
            self.update()
            self.last_update_step = self.train_step

    def save_model(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        th.save(self.Q.state_dict(), path + 'Q' +'.pth')


    def load_model(self, path):
        file = path + 'Q.pth'
        if not os.path.isfile(file):
            print("here have not such model")
            return
        self.Q.load_state_dict(th.load(file, map_location=th.device('cpu')))
        self.target_Q.load_state_dict(self.Q.state_dict())
        print('sucess load the model in ', file)
        return

