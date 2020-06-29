import torch.nn as nn
import torch.nn.functional as F
import torch as th


class DNNAgent(nn.Module):
    def __init__(self, param_set):
        super(DNNAgent, self).__init__()
        self.param_set = param_set

        self.hidden_dim = param_set['hidden_dim']
        if param_set['ob_style'] == 'primitive':
            self.input_len = param_set['obs_shape']
        elif param_set['ob_style'] == 'concat':
            self.input_len = param_set['obs_shape'] * 2
        self.output_len = param_set['n_actions']
        self.hidden_layer = param_set['hidden_layer']

        self.obs_encoder = nn.Linear(self.input_len, param_set['obs_hidden_dim'])
        self.action_encoder = nn.Linear(param_set['n_actions'], param_set['action_hidden_dim'])
        self.concat_encoder = nn.Linear(param_set['obs_hidden_dim']+ param_set['action_hidden_dim'],self.hidden_dim )

        for i in range(self.hidden_layer):
            setattr(self, 'fc%s' % i, nn.Linear(self.hidden_dim, self.hidden_dim))
        self.decode = nn.Linear(self.hidden_dim, self.output_len)


    def forward(self, obs, action_prob):
        # print(inputs.shape, self.input_len)
        h_obs = F.relu(self.obs_encoder(obs))
        h_act = F.relu(self.action_encoder(action_prob))
        h_concat = th.cat([h_obs, h_act], dim=-1)
        x = F.relu(self.concat_encoder(h_concat))
        for i in range(self.hidden_layer):
            net = getattr(self, 'fc%s' % i, )
            x = F.relu(net(x))
        x = th.tanh(self.decode(x))
        return x
