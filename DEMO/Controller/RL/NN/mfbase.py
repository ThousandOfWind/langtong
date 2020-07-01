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
        elif param_set['ob_style'] == 'lstm':
            self.input_len = param_set['obs_shape']
            self.rnn = nn.GRUCell(self.obs_hidden_dim, self.obs_hidden_dim)
        self.output_len = param_set['n_actions']
        self.hidden_layer = param_set['hidden_layer']

        self.obs_encoder = nn.Linear(self.input_len, param_set['obs_hidden_dim'])
        self.action_encoder = nn.Linear(self.output_len, param_set['action_hidden_dim'])
        self.concat_encoder = nn.Linear(param_set['obs_hidden_dim']+ param_set['action_hidden_dim'],self.hidden_dim )

        for i in range(self.hidden_layer):
            setattr(self, 'fc%s' % i, nn.Linear(self.hidden_dim, self.hidden_dim))
        self.decode = nn.Linear(self.hidden_dim, self.output_len)


    def forward(self, obs, lio, action_prob):

        if self.ob_style == 'primitive':
            h_obs = F.relu(self.obs_encoder(obs))
        elif self.ob_style == 'concat':
            obs = th.cat([obs, lio], dim=-1)
            h_obs = F.relu(self.obs_encoder(obs))
        elif self.ob_style == 'lstm':
            bs = lio.shape[0]
            h_lio = F.relu(self.obs_encoder(lio))

            if self.on_cuda:
                h = th.zeros((bs, self.hidden_dim)).cuda()
            else:
                h = th.zeros((bs, self.hidden_dim))

            h = F.relu(self.rnn(h_lio, h))
            h_obs = F.relu(self.obs_encoder(obs))
            h_obs = F.relu(self.rnn(h_obs, h))


        # print(obs.shape, action_prob.shape, self.output_len)
        h_act = F.relu(self.action_encoder(action_prob))
        h_concat = th.cat([h_obs, h_act], dim=-1)
        x = F.relu(self.concat_encoder(h_concat))
        for i in range(self.hidden_layer):
            net = getattr(self, 'fc%s' % i, )
            x = F.relu(net(x))
        x = th.tanh(self.decode(x))
        return x
