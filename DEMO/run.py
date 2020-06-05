import argparse
from tensorboardX import SummaryWriter
import os
import torch
import random
import numpy as np

from MDP.modules_v2 import DECISION_INTERVAL
from data.read import MATERIAL, STAGE, order_craft, STAGE_name, Artificial_STAGE_name, Artificial_STAGE
from Controller.agents import init_Agents
from MemoryBuffer.Memory import MemoryBuffer
from MDP.reward import REWARD_RUlE


parser = argparse.ArgumentParser(description="tranaction")
parser.add_argument("--cuda", action="store_true", help="Use cuda?")
parser.add_argument("--gpus", default="0", type=str, help="gpu ids (default: 0)")
parser.add_argument("--nEpochs", type=int, default=1, help="Number of epochs to train for")
parser.add_argument("--nEpisode", type=int, default=500000, help="Number of epochs to train for")
parser.add_argument("--agentType", default="RL", type=str, help="agentType")
parser.add_argument('--pretrained', default='', type=str, help='path to pretrained model (default: none)')
parser.add_argument("--mamory_size", type=int, default=50000, help="Test Frequncy")
parser.add_argument("--batchSize", type=int, default=128, help="Training batch size")
parser.add_argument("--lr", type=float, default=0.0005, help="Learning Rate. Default=0.0005")
parser.add_argument("--etl", type=int, default=10000, help="epsilon_time_length default=3000 from 1 - 0.01")
parser.add_argument("--gamma", type=float, default=0.8, help="GAMMA. Default=0.8")
parser.add_argument("--tui", type=int, default=200, help="target update interval. Default=200")


Peice = 60 * 8
Day = 3
TIMELIMIT = 7 * 24 * 60


def tToClock(t):
    p = t // Peice
    p = p % Day
    return p


# MDP
def episode(memoryBuffer, all_agents,e,std_out_type):
    t = 0

    while True:
        p = tToClock(t)
        # 首先是订单stage,
        if order_craft.order_act(time_step=t, materials=MATERIAL):
            memoryBuffer.add_reward((TIMELIMIT - t ) * REWARD_RUlE['success'])
            if std_out_type['result']:
                print('epsode', e, 'success at step', t, 'win', (TIMELIMIT - t ))
            break

        # 自上而下的决策stage
        # for stage_id in stage_names:
        #     STAGE[s_id].set_demand()
        #     stages[stage_id].stage_sequantial_step(agents=all_agents[stage_id], memoryBuffer=memoryBuffer, clock=p, t=t, log=True)

        for s_id in STAGE_name:
            STAGE[s_id].set_demand(MATERIAL)
        for s_id in Artificial_STAGE_name:
            Artificial_STAGE[s_id].stage_sequantial_step(agents=all_agents[s_id], memoryBuffer=memoryBuffer, clock=p,
                                                         t=t, materials=MATERIAL, e=e,std_out_type=std_out_type)

        for m_id in MATERIAL.keys():
            if type(MATERIAL[m_id]) == dict:
                for o_id in MATERIAL[m_id].keys():
                    MATERIAL[m_id][o_id].clear()
            else:
                MATERIAL[m_id].clear()

        t += DECISION_INTERVAL
        if t > TIMELIMIT:
            memoryBuffer.add_reward(REWARD_RUlE['fail'] * order_craft.remain_order_demand())
            if std_out_type['result']:
                print('epsode', e, 'fail and remain', order_craft.remain_order_demand())
            break


def run(param_set):
    std_out_type = {
        'device_action': False,
        'stage_step': True,
        'result': True
    }

    param_set['random_seed'] = random.randint(0, 1000)
    np.random.seed(param_set['random_seed'])
    torch.manual_seed(param_set['random_seed'])
    if param_set['cuda'] :
        torch.cuda.manual_seed(param_set['random_seed'])

    path = param_set['path'] + str(param_set['random_seed']) + '/'
    writer = SummaryWriter('logs' + path)
    memoryBuffer = MemoryBuffer(param_set)

    # 初始化agents
    all_agents = {}
    for stage_id in Artificial_STAGE_name:
        param = param_set.copy()
        param['path'] = 'model' + path + stage_id + '/'
        param.update(Artificial_STAGE[stage_id].info())
        agent_id_list = [d.id for d in Artificial_STAGE[stage_id].devices]
        agents = init_Agents(param_set=param, agent_id_list=agent_id_list, writer=writer)
        all_agents[stage_id] = agents

    for e in range(param_set['n_episodes']):
        episode(memoryBuffer=memoryBuffer, all_agents=all_agents, e=e, std_out_type=std_out_type)
        memoryBuffer.end_trajectory()
        if e > 2:
            for stage_id in Artificial_STAGE_name:
                all_agents[stage_id].learn(memory=memoryBuffer, episode=e)


if __name__ == '__main__':

    global opt
    opt = parser.parse_args()

    cuda = opt.cuda
    if cuda:
        print("=> use gpu id: '{}'".format(opt.gpus))
        os.environ["CUDA_VISIBLE_DEVICES"] = opt.gpus
        if not torch.cuda.is_available():
            raise Exception("No GPU found or Wrong gpu id, please run without --cuda")
    # _test()

    param_set = {}
    param_set['agentType'] = opt.agentType

    param_set['cuda'] = opt.cuda
    param_set['n_epochs'] = opt.nEpochs
    param_set['n_episodes'] = opt.nEpisode
    param_set['mamory_size'] = opt.mamory_size
    param_set['batch_size'] = opt.batchSize
    param_set['gamma'] = opt.gamma
    param_set['learning_rate'] = opt.lr
    param_set['time_length'] = opt.etl
    param_set['epsilon_start'] = 1
    param_set['epsilon_end'] = 0
    param_set['grad_norm_clip'] = 10
    param_set['target_update_interval'] = opt.tui
    param_set['load_model'] = False
    # param_set['tau'] = 0.01
    param_set['hidden_dim'] = 64
    param_set['hidden_layer'] = 1

    path = '/etl'+str(param_set['time_length'])[:-3]+'k-'+ str(param_set['epsilon_start']) + str(param_set['epsilon_end']) + \
           'lr'+ str(param_set['learning_rate'])[2:]+ 'clip' + str(param_set['grad_norm_clip']) + \
           '-m' + str(param_set['mamory_size'])[:-3] + 'k-bs' + str(param_set['batch_size']) + \
           '-g' + str(param_set['gamma'])[2:] + '-tui' + str(param_set['target_update_interval']) + \
           '-hd' + str(param_set['hidden_dim']) + '-hl' + str(param_set['hidden_layer']) + '/'

    param_set['path'] = path

    for _ in range(param_set['n_epochs']):
        run(param_set)
