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
        if self.ob_style in ['primitive', 'concat']:
            self.Q = NN['DNN'](param_set)
        elif self.ob_style == 'lstm':
            self.Q = NN['seqLSTM'](param_set)

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

    def approximate_Q(self, obs, lio):
        device = th.device("cuda" if th.cuda.is_available() else "cpu")
        obs = th.FloatTensor(obs).to(device).reshape(1,-1)
        if self.ob_style == 'primitive':
            q = self.Q(obs)
        elif self.ob_style == 'concat':
            lio = th.FloatTensor(lio).to(device).reshape(1,-1)
            input = th.cat([lio,obs],-1)
            q = self.Q(input)
        elif self.ob_style == 'lstm':
            lio = th.FloatTensor(lio).to(device).reshape(1,-1)
            q = self.Q(lio, obs)

        return q

    def train(self, batch, episode):
        # batch * agent , t
        device = th.device("cuda" if th.cuda.is_available() else "cpu")

        self.train_step += 1
        reward = th.FloatTensor(batch["reward"]).to(device)
        action = th.LongTensor(batch["action"]).to(device)
        done = th.FloatTensor(batch["done"]).to(device)
        obs = th.FloatTensor(batch["obs"]).to(device)
        lio = th.FloatTensor(batch["last_iobs"]).to(device)
        next_obs = th.FloatTensor(batch["next_obs"]).to(device)
        next_lio = th.FloatTensor(batch["iobs"]).to(device)
        next_avail_action = th.FloatTensor(batch['next_avail_action']).to(device)

        shuffle_index = np.random.choice(reward.shape[0], batch["bs"] * 100)
        rd.shuffle(shuffle_index)
        shuffle_index = th.from_numpy(shuffle_index).to(device)
        reward = reward.gather(dim=0, index=shuffle_index)
        action = action.gather(dim=0, index=shuffle_index)
        done = done.gather(dim=0, index=shuffle_index)
        obs = obs.gather(dim=0, index=shuffle_index.reshape(-1,1).repeat(1,obs.shape[1]))
        next_obs = next_obs.gather(dim=0, index=shuffle_index.reshape(-1,1).repeat(1,next_obs.shape[1]))
        next_avail_action = next_avail_action.gather(dim=0, index=shuffle_index.reshape(-1,1).repeat(1,next_avail_action.shape[1]))
        lio = lio.gather(dim=0, index=shuffle_index.reshape(-1,1).repeat(1,obs.shape[1]))
        next_lio = next_lio.gather(dim=0, index=shuffle_index.reshape(-1,1).repeat(1,obs.shape[1]))

        if self.ob_style == 'primitive':
            q = self.Q(obs)
        elif self.ob_style == 'concat':
            input = th.cat([lio,obs], -1)
            q = self.Q(input)
        elif self.ob_style == 'lstm':
            q = self.Q(lio, obs)

        chosen_action_qvals = th.gather(q, dim=1, index=action.unsqueeze(-1)).squeeze(-1)

        if self.ob_style == 'primitive':
            next_q = self.target_Q(next_obs)
        elif self.ob_style == 'concat':
            input = th.cat([next_lio,next_obs], -1)
            next_q = self.Q(input)
        elif self.ob_style == 'lstm':
            next_q = self.Q(next_lio, next_obs)

        next_q[next_avail_action == 0] = -9999
        next_max_q, _ = next_q.max(dim=1)

        targets = (reward + self.gamma * (1 - done) * next_max_q).detach()
        loss = ((chosen_action_qvals - targets) ** 2).sum()

        self.writer.add_scalar('Loss/TD_loss_' + self.name, loss.item(), episode)

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

