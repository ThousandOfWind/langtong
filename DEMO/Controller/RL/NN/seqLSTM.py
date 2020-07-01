import torch.nn as nn
import torch.nn.functional as F
import torch as th


class DNNAgent(nn.Module):
    def __init__(self, param_set):
        super(DNNAgent, self).__init__()
        self.param_set = param_set
        self.on_cuda = param_set['cuda']

        self.hidden_dim = param_set['hidden_dim']
        self.input_len = param_set['obs_shape']
        self.output_len = param_set['n_actions']
        self.hidden_layer = param_set['hidden_layer']

        self.lio = param_set['lio']

        self.encode = nn.Linear(self.input_len, self.hidden_dim)
        self.rnn = nn.GRUCell(self.hidden_dim, self.hidden_dim)

        for i in range(self.hidden_layer):
            setattr(self, 'fc%s' % i, nn.Linear(self.hidden_dim, self.hidden_dim))
        self.decode = nn.Linear(self.hidden_dim, self.output_len)


    def forward(self, lio, obs):
        bs = lio.shape[0]
        l = F.relu(self.encode(lio))
        if self.on_cuda:
            h = th.zeros((bs, self.hidden_dim)).cuda()
        h = F.relu(self.rnn(l,h))

        x = F.relu(self.encode(obs))
        # print(lio.shape, h.shape,x.shape)
        x = F.relu(self.rnn(x,h))
        for i in range(self.hidden_layer):
            net = getattr(self, 'fc%s' % i, )
            x = F.relu(net(x))
        x = th.tanh(self.decode(x))
        return x
