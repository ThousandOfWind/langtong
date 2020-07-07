import torch.nn as nn
import torch.nn.functional as F
import torch as th


class DNNAgent(nn.Module):
    def __init__(self, param_set):
        super(DNNAgent, self).__init__()
        self.param_set = param_set

        self.hidden_dim = param_set['hidden_dim']
        self.obs_hidden_dim = param_set['obs_hidden_dim']
        self.on_cuda = param_set['cuda']

        self.ob_style = param_set['ob_style']
        if param_set['ob_style'] == 'primitive':
            self.input_len = param_set['obs_shape']
        elif param_set['ob_style'] == 'concat':
            self.input_len = param_set['obs_shape'] * 2

        self.rnn = nn.GRUCell(self.obs_hidden_dim, self.obs_hidden_dim)
        self.output_len = param_set['n_actions']
        self.hidden_layer = param_set['hidden_layer']

        self.obs_encoder = nn.Linear(self.input_len, param_set['obs_hidden_dim'])
        self.action_encoder = nn.Linear(self.output_len, param_set['action_hidden_dim'])
        self.concat_encoder = nn.Linear(param_set['obs_hidden_dim']+ param_set['action_hidden_dim'],self.hidden_dim )

        for i in range(self.hidden_layer):
            setattr(self, 'fc%s' % i, nn.Linear(self.hidden_dim, self.hidden_dim))
        self.decode = nn.Linear(self.hidden_dim, self.output_len)


    def init_hidden(self):
        # make hidden states on same device as model
        if self.on_cuda:
            return th.zeros((1,self.hidden_dim)).cuda()
        else:
            return th.zeros((1,self.hidden_dim))

    def forward(self, obs, action_prob, hidden_state):
        h_obs = F.relu(self.obs_encoder(obs))
        h_in = hidden_state.reshape(-1, self.hidden_dim)
        h_obs = F.relu(self.rnn(h_obs, h_in))

        # print(obs.shape, action_prob.shape, self.output_len)
        h_act = F.relu(self.action_encoder(action_prob))
        h_concat = th.cat([h_obs, h_act], dim=-1)
        x = F.relu(self.concat_encoder(h_concat))
        for i in range(self.hidden_layer):
            net = getattr(self, 'fc%s' % i, )
            x = F.relu(net(x))
        x = th.tanh(self.decode(x))
        return x, h_obs
