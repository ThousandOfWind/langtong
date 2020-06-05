import copy
import torch as th
from torch.optim import Adam
from torch.optim import RMSprop

import os
from torchvision.utils import make_grid
import torch.nn as nn
from torchvision import transforms
from PIL import Image

from .model import DNNAgent as DNN

class QLearner:
    """
    1. DQN- RNNAgent
    2. train
    """
    def __init__(self,param_set, writer):
        self.obs_shape = param_set['obs_shape']
        self.gamma = param_set['gamma']
        self.learning_rate = param_set['learning_rate']
        self.grad_norm_clip = param_set['grad_norm_clip']

        self.Q = DNN(param_set)
        if param_set['cuda']:
            self.Q.cuda()
        self.params = self.Q.parameters()
        self.target_Q = copy.deepcopy(self.Q)

        self.optimiser = Adam(params=self.params, lr=self.learning_rate)
        self.train_step = 0
        self.last_update_step = 0
        self.update_frequncy = param_set['target_update_interval']
        self.writer = writer

    def update(self):
        self.target_Q.load_state_dict(self.Q.state_dict())

    def approximate_Q(self, obs):
        device = th.device("cuda" if th.cuda.is_available() else "cpu")
        obs = th.FloatTensor(obs).to(device)
        return self.Q(obs)

    def train(self, batch, episode):
        # batch * agent , t
        device = th.device("cuda" if th.cuda.is_available() else "cpu")

        self.train_step += 1
        reward = th.FloatTensor(batch["reward"]).to(device)
        action = th.LongTensor(batch["action"]).to(device)
        done = th.FloatTensor(batch["done"]).to(device)
        obs = th.FloatTensor(batch["obs"]).to(device)
        next_obs = th.FloatTensor(batch["next_obs"]).to(device)
        next_avail_action = th.FloatTensor(batch['next_avail_action']).to(device)


        q = self.Q(obs)
        chosen_action_qvals = th.gather(q, dim=1, index=action.unsqueeze(-1)).squeeze(-1)

        next_q = self.target_Q(next_obs)
        next_q[next_avail_action == 0] = -9999
        next_max_q, _ = next_q.max(dim=1)

        targets = (reward + self.gamma * (1 - done) * next_max_q).detach_()
        loss = ((chosen_action_qvals - targets) ** 2).sum()

        self.writer.add_scalar('Loss/TD_loss', loss.item(), episode)

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


