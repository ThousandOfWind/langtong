import argparse
from tensorboardX import SummaryWriter
import os
import torch
import random
import numpy as np

from MDP.modules_v2 import DECISION_INTERVAL
from data.read import MATERIAL, STAGE, STAGE_name, Artificial_STAGE_name, Artificial_STAGE, DEVICE, get_oder, curriculum_order
from Controller.curriculum_schdule import CURs
from data.create_map import Equipment_Relation_Map
from Controller.agents import init_Agents
from MemoryBuffer.Memory import MemoryBuffer
from MDP.reward import REWARD_RUlE


parser = argparse.ArgumentParser(description="langtong")
parser.add_argument("--cuda", action="store_true", help="Use cuda?")
parser.add_argument("--gpus", default="2", type=str, help="gpu ids (default: 2)")
parser.add_argument("--nEpochs", type=int, default=1, help="Number of epochs to train for")
parser.add_argument("--nEpisode", type=int, default=5000000, help="Number of epochs to train for")
parser.add_argument("--agentType", default="MF", type=str, help="agentType")
parser.add_argument("--rewardType", default="mnp", type=str, help="rewardType")
parser.add_argument('--pretrained', default='', type=str, help='path to pretrained model (default: none)')
parser.add_argument("--mamorySize", type=int, default=1000, help="mamorySize")
parser.add_argument("--batchSize", type=int, default=2, help="Training batch size")
parser.add_argument("--lr", type=float, default=5e-5, help="Learning Rate. Default=0.0005")
parser.add_argument("--etl", type=int, default=100, help="epsilon_time_length default=3000 from estart - eend")
parser.add_argument("--estart", type=float, default=1, help="epsilon_time_length default=3000 from estart - eend")
parser.add_argument("--eend", type=float, default=0, help="epsilon_time_length default=3000 from estart - eend")
parser.add_argument("--gamma", type=float, default=0.99, help="GAMMA. Default=0.8")
parser.add_argument("--tui", type=int, default=200, help="target update interval. Default=200")
parser.add_argument("--delay", type=int, default=1, help="extend time for product. Default=2")
parser.add_argument("--hiddenDim", type=int, default=64, help="hidden dim of network. Default=64")
parser.add_argument("--obs_hidden_dim", type=int, default=64, help="hidden dim of network. Default=64")
parser.add_argument("--action_hidden_dim", type=int, default=32, help="hidden dim of network. Default=64")
parser.add_argument("--hiddenLay", type=int, default=2, help="hidden layer of network. Default=2")
parser.add_argument("--obStyle", type=str, default='lstm', help="primitive, concat, lstm")
parser.add_argument("--obId", action="store_true", help="Use agentID?")

parser.add_argument("--curriculumStyle", type=str, default='base', help="level of task difficulty")
parser.add_argument("--curriculumTL", type=int, default=200, help="timelength of each curriculum")
parser.add_argument("--curriculumEnd", type=str, default='fix', help="fix / loss")
parser.add_argument("--curriculumMemory", type=str, default='private', help="private / share")
parser.add_argument("--curriculum", action="store_true", help="Use curriculum")


Peice = 60 * 8
Day = 3
# TIMELIMIT = 7 * 24 * 60
TIMELIMIT = 3000


def tToClock(t):
    p = t // Peice
    p = p % Day
    return p


# MDP
def episode(memoryBuffer, all_agents,e,std_out_type, writer, reward_rule, delay, oc, task):
    t = 0

    while True:
        p = tToClock(t)
        # 首先是订单stage,
        if oc.order_act(time_step=t, materials=MATERIAL, std_out_type=std_out_type) :
            final_rew = max(0, (TIMELIMIT - t ) * reward_rule['reduce_time']) + reward_rule['success']
            memoryBuffer.add_reward(final_rew)
            if std_out_type['result']:
                print(task,'epsode', e, 'success at step', t, 'win', (TIMELIMIT - t ))
            writer.add_scalar('result/'+ task +'cost_time', t, e)
            writer.add_scalar('result/'+ task +'remain_oder', 0, e)
            return t, final_rew

        # 自上而下的决策stage
        # for stage_id in stage_names:
        #     STAGE[s_id].set_demand()
        #     stages[stage_id].stage_sequantial_step(agents=all_agents[stage_id], memoryBuffer=memoryBuffer, clock=p, t=t, log=True)

        for s_id in STAGE_name:
            STAGE[s_id].set_demand(MATERIAL)
        for s_id in Artificial_STAGE_name:
            Artificial_STAGE[s_id].stage_sequantial_step(agents=all_agents[s_id], memoryBuffer=memoryBuffer, clock=p,
                                                         t=t, materials=MATERIAL, e=e,std_out_type=std_out_type, reward_rule=reward_rule)

        for m_id in MATERIAL.keys():
            if type(MATERIAL[m_id]) == dict:
                for o_id in MATERIAL[m_id].keys():
                    MATERIAL[m_id][o_id].clear()
            else:
                MATERIAL[m_id].clear()

        t += DECISION_INTERVAL

        if t >= delay * TIMELIMIT:
            remain_order = oc.remain_order_demand()
            final_rew = reward_rule['fail-order'] * remain_order + reward_rule['fail']
            memoryBuffer.add_reward(final_rew)
            if std_out_type['result']:
                print(task,'epsode', e, 'fail and remain', remain_order)
            writer.add_scalar('result/'+ task +'cost_time', t, e)
            writer.add_scalar('result/'+ task +'remain_oder', 0, e)
            return t, final_rew

        if t >= TIMELIMIT:
            memoryBuffer.add_reward(oc.remain_order_demand() * reward_rule['exceed-time'])
            memoryBuffer.add_reward(oc.remain_order_demand() * reward_rule['remain-order'])




def run(param_set):
    std_out_type = {
        'device_action': False,
        'stage_step': True,
        'result': True,
        'matrial': False,
        'Q': False
    }

    reward_rule = REWARD_RUlE[param_set['reward_Type']]

    param_set['random_seed'] = random.randint(0, 1000)
    np.random.seed(param_set['random_seed'])
    torch.manual_seed(param_set['random_seed'])
    if param_set['cuda'] :
        torch.cuda.manual_seed(param_set['random_seed'])

    path = param_set['path'] + str(param_set['random_seed']) + '/'
    writer = SummaryWriter('logs/' + path)
    memoryBuffer = MemoryBuffer(param_set)
    delay = param_set['delay']

    # 初始化agents
    all_agents = {}
    for stage_id in Artificial_STAGE_name:
        Artificial_STAGE[stage_id].obId = param_set['obId']
        param = param_set.copy()
        param['path'] = 'model' + path + stage_id + '/'
        param.update(Artificial_STAGE[stage_id].info())
        agent_id_list = [d.id for d in Artificial_STAGE[stage_id].devices]
        agents = init_Agents(param_set=param, agent_id_list=agent_id_list, writer=writer, name=stage_id, map=Equipment_Relation_Map)
        all_agents[stage_id] = agents

    acummulateE = 0
    if param_set['curriculum']:
        curs = CURs[param_set['cS']]

        for cur in curs:
            task = ''.join([str(int(t)) for t in cur[0]]) + str(cur[1])
            if param_set['cM'] == 'private':
                curMB = MemoryBuffer(param_set)
            else:
                curMB = memoryBuffer
            for e in range(param_set['cT']):
                om, oc = curriculum_order(cur[0], cur[1])
                # print(task, oc.__str__())
                episode(memoryBuffer=curMB, all_agents=all_agents, e=e, std_out_type=std_out_type,
                        writer=writer, reward_rule=reward_rule, delay=delay, oc=oc, task=task)
                curMB.end_trajectory()

                for o_id in om:
                    writer.add_scalar(task + '-order/' + o_id, om[o_id].bom[0][1], e)

                for d_id in DEVICE.keys():
                    DEVICE[d_id].reset()

                for m_id in MATERIAL.keys():
                    if type(MATERIAL[m_id]) == dict:
                        for o_id in MATERIAL[m_id].keys():
                            MATERIAL[m_id][o_id].reset()
                    else:
                        MATERIAL[m_id].reset()

                # for o_id in om:
                #     om[o_id].reset()
                # oc.reset()

                if (param_set['cM'] == 'private' and e > param_set['batch_size']) \
                        or (param_set['cM'] == 'share' and (acummulateE + e) > param_set['batch_size']):
                    for stage_id in Artificial_STAGE_name:
                        all_agents[stage_id].learn(memory=curMB, episode=acummulateE + e)
            acummulateE += param_set['cT']
        del curMB


    t_min = delay * TIMELIMIT
    result_path = 'result' + path
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    for e in range(param_set['n_episodes']):
        om, oc = get_oder()

        this_t, final_rew = episode(memoryBuffer=memoryBuffer, all_agents=all_agents, e=acummulateE + e, std_out_type=std_out_type,
                            writer=writer, reward_rule=reward_rule, delay=delay, oc=oc, task='target')
        memoryBuffer.end_trajectory()

        if this_t < t_min:
            print('\tsave!')
            t_min = this_t
            for d_id in DEVICE.keys():
                DEVICE[d_id].save(result_path)
        for d_id in DEVICE.keys():
            writer.add_scalar('device-accumulateReward/' + d_id, DEVICE[d_id].accumulateReward, acummulateE + e)
            writer.add_scalar('device-accumulateRewardwithFinal/' + d_id, DEVICE[d_id].accumulateReward + final_rew, acummulateE + e)
            writer.add_scalar('device-accumulateWaitTime/' + d_id, DEVICE[d_id].accumulateWaitTime, acummulateE + e)
        for o_id in om:
            writer.add_scalar('target-order/' + o_id, om[o_id].bom[0][1], acummulateE + e)

        for d_id in DEVICE.keys():
            DEVICE[d_id].reset()

        for m_id in MATERIAL.keys():
            if type(MATERIAL[m_id]) == dict:
                for o_id in MATERIAL[m_id].keys():
                    MATERIAL[m_id][o_id].reset()
            else:
                MATERIAL[m_id].reset()

        if param_set['curriculum']:
            if (param_set['cM'] == 'private' and e > param_set['batch_size']) \
                    or (param_set['cM'] == 'share' and (acummulateE + e) > param_set['batch_size']):
                for stage_id in Artificial_STAGE_name:
                    all_agents[stage_id].learn(memory=memoryBuffer, episode=acummulateE + e)
        else:
            if ( e > param_set['batch_size']) :
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
    param_set['max_seq_len'] = TIMELIMIT // DECISION_INTERVAL

    param_set['agentType'] = opt.agentType

    param_set['cuda'] = opt.cuda
    param_set['n_epochs'] = opt.nEpochs
    param_set['n_episodes'] = opt.nEpisode
    param_set['mamory_size'] = opt.mamorySize
    param_set['batch_size'] = opt.batchSize
    param_set['gamma'] = opt.gamma
    param_set['learning_rate'] = opt.lr
    param_set['time_length'] = opt.etl
    param_set['epsilon_start'] = opt.estart
    param_set['epsilon_end'] = opt.eend

    param_set['grad_norm_clip'] = 10
    param_set['target_update_interval'] = opt.tui
    param_set['load_model'] = False
    # param_set['tau'] = 0.01
    param_set['hidden_dim'] = opt.hiddenDim
    param_set['hidden_layer'] = opt.hiddenLay
    param_set['delay'] = opt.delay
    param_set['reward_Type'] = opt.rewardType
    param_set['obs_hidden_dim'] = opt.obs_hidden_dim
    param_set['action_hidden_dim'] = opt.action_hidden_dim


    # 'primitive', 'concat', 'lstm'
    param_set['ob_style'] = opt.obStyle
    param_set['obId'] = opt.obId

    param_set['curriculum'] = opt.curriculum
    if param_set['curriculum']:
        param_set['cS'] = opt.curriculumStyle
        param_set['cT'] = opt.curriculumTL
        param_set['cE'] = opt.curriculumEnd
        param_set['cM'] = opt.curriculumMemory
        strC = '-curriculum' + param_set['cS'] + '-cT' + str(param_set['cT']) + '-end' + param_set['cE'] + '-cM' + param_set['cM']
    else:
        strC = ''


    path = '/mf' + strC + \
           '/etl'+str(param_set['time_length'])+'-'+ str(param_set['epsilon_start']) + str(param_set['epsilon_end']) + \
           '/m' + str(param_set['mamory_size'])[:-3] + 'k-bs' + str(param_set['batch_size']) + '-tui' + str(param_set['target_update_interval']) + \
           '/g' + str(param_set['gamma'])[2:] + '-REW' + param_set['reward_Type'] + '-delay'+ str(param_set['delay'])+  \
           '-lr'+ str(param_set['learning_rate'])+ '-clip' + str(param_set['grad_norm_clip']) + \
           '/obs' + param_set['ob_style'] + ('-obId' if param_set['obId'] else '') + '-o' + str(param_set['obs_hidden_dim'])  + '-a' + str(param_set['action_hidden_dim'])  + '-hd' + str(param_set['hidden_dim']) + '-hl' + str(param_set['hidden_layer']) + '/'

    param_set['path'] = path


    for _ in range(param_set['n_epochs']):
        run(param_set)
