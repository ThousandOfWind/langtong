import csv
import random
import copy
import numpy as np
import torch as th


class MemoryBuffer:
    def __init__(self, param_set):
        self.buffer = []
        self.current = {}
        self.mamory_size = param_set['mamory_size']
        self.path = 'data/' + param_set['path']
        self.max_seq_len = param_set['max_seq_len']


    def end_trajectory(self):
        self.buffer.append(self.current)
        if len(self.buffer) > self.mamory_size:
            self.buffer = self.buffer[1:]
        self.current = {}

    def append(self, experience):
        """
        :param experience = {
                "id": device.id,
                "step": t,
                "state": state,
                "available_action": available_action,
                "action": action,
                "action_index": action_index,
                "reward": reward
            }
        :return:
        """
        if experience['id'] in self.current.keys():
            self.current[experience['id']]["obs"].append(experience["obs"])
            self.current[experience['id']]["immediately_obs"].append(experience["immediately_obs"])
            self.current[experience['id']]["available_action"].append(experience["available_action"])
            # self.current[experience['id']]["action"].append(experience["action"])
            self.current[experience['id']]["action_index"].append(experience["action_index"])
            self.current[experience['id']]["reward"].append(experience["reward"])

        else:
            self.current[experience['id']] = {
                "obs": [experience["obs"]],
                "immediately_obs": [experience["immediately_obs"]],
                "available_action": [experience['available_action']],
                # "action": [experience['action']],
                "action_index": [experience['action_index']],
                "reward": [experience['reward']]
            }

    def sample(self, idList:[], batchSize:int, mf=False, map=None):

        batch ={
            'obs': [[] for _ in idList],
            'action': [[] for _ in idList],
            'reward': [[] for _ in idList],
            'done':[[] for _ in idList],
            'next_obs': [[] for _ in idList],
            'next_avail_action': [[] for _ in idList],
            'last_iobs': [[] for _ in idList],
            'iobs': [[] for _ in idList],
            'mean_action': [[] for _ in idList],
            'last_mean_action': [[] for _ in idList],
            'bs': len(idList) * batchSize,
        }

        action = {d_id:{} for d_id in idList}


        for item in range(batchSize):
            b_id = random.randint(0, len(self.buffer)-1)
            for index, d_id in enumerate(idList):
                batch['obs'][index] += copy.deepcopy(self.buffer[b_id][d_id]['obs'])
                batch['reward'][index]  += copy.deepcopy(self.buffer[b_id][d_id]['reward'])
                batch['action'][index]  += copy.deepcopy(self.buffer[b_id][d_id]['action_index'])
                batch['done'][index]  += ([0,]*(len(self.buffer[b_id][d_id]['action_index'])-1)+[1,])
                next = copy.deepcopy(self.buffer[b_id][d_id]['obs'][1:])
                next.append([0]* len(self.buffer[b_id][d_id]['obs'][0]))
                batch['next_obs'][index]  += next
                next_avail = copy.deepcopy(self.buffer[b_id][d_id]['available_action'][1:])
                next_avail.append([0]* len(self.buffer[b_id][d_id]['available_action'][0]))
                batch['next_avail_action'][index]  += (next_avail)

                batch['iobs'][index]  += copy.deepcopy(self.buffer[b_id][d_id]['immediately_obs'])
                last_iobs = self.buffer[b_id][d_id]['immediately_obs'][0:1] + self.buffer[b_id][d_id]['immediately_obs'][:-1]
                batch['last_iobs'][index] += copy.deepcopy(last_iobs)

                if mf:
                    device = th.device("cuda" if th.cuda.is_available() else "cpu")
                    one_hot = th.zeros((len(self.buffer[b_id][d_id]['action_index']), len(self.buffer[b_id][d_id]['available_action'][0]))).to(device)
                    action_index = th.LongTensor(self.buffer[b_id][d_id]['action_index']).to(device)
                    action[d_id][item] = one_hot.scatter(1, action_index.unsqueeze(1), 1)

        if mf:
            for index, d_id in enumerate(idList):
                for item in range(batchSize):
                    mean_action = th.zeros_like(action[d_id][item])
                    for nei in map[d_id]['Counterparts']:
                        # print(mean_action.shape, action[nei][item].shape)
                        mean_action += action[nei][item]
                    mean_action /= len(map[d_id]['Counterparts'])

                    batch['mean_action'][index].append(copy.deepcopy(mean_action))
                    batch['last_mean_action'][index].append(th.zeros((1, mean_action.shape[-1])).to(device))
                    batch['last_mean_action'][index].append(copy.deepcopy(mean_action[:-1]))
                batch['mean_action'][index] = th.cat(batch['mean_action'][index], dim=0).to(device)
                batch['last_mean_action'][index] = th.cat(batch['last_mean_action'][index], dim=0).to(device)
            batch['mean_action'] = th.stack(batch['mean_action'], dim=0).to(device)
            batch['last_mean_action'] = th.stack(batch['last_mean_action'], dim=0).to(device)

        batch['obs'] = th.FloatTensor(batch['obs']).to(device)
        batch['reward'] = th.FloatTensor(batch['reward']).to(device)
        batch['action'] = th.LongTensor(batch["action"]).to(device)
        batch['done'] = th.FloatTensor(batch["done"]).to(device)
        batch['next_obs'] = th.FloatTensor(batch["next_obs"]).to(device)
        batch['next_avail_action'] = th.FloatTensor(batch["next_avail_action"]).to(device)
        batch['last_iobs'] = th.FloatTensor(batch["last_iobs"]).to(device)
        # batchaction_index['iobs'] = th.FloatTensor(batch["iobs"]).to(device)                                                                      :-1]
        return batch

    def get_current(self, d_id, item,  map=None):

        if item == 'last_mean_action':
            if d_id in self.current:
                mean = th.zeros(len(self.current[d_id]['available_action'][-1]))
                for nei in map[d_id]['Counterparts']:
                    mean[self.current[nei]['action_index'][-1]] += 1
                mean /= len(map[d_id]['Counterparts'])
                return True, mean
            else:
                return False, None

        if d_id in self.current:
            return True, self.current[d_id][item][-1]
        return False, None

    def get_current_trajectory(self, d_id,  map=None):
        device = th.device("cuda" if th.cuda.is_available() else "cpu")
        if d_id in self.current:
            batch = {}
            batch['bs'] = 1
            batch['obs'] = th.FloatTensor(self.current[d_id]['obs'])
            batch['lio'] = th.FloatTensor(self.current[d_id]['obs'][0:1] + self.current[d_id]['immediately_obs'])
            if d_id in self.current:
                mean = th.zeros((len(self.current[d_id]['available_action']), len(self.current[d_id]['available_action'][-1]))).to(device)
                for nei in map[d_id]['Counterparts']:
                    one_hot = th.zeros_like(mean).to(device)
                    action_index = th.LongTensor(self.current[nei]['action_index']).to(device)
                    mean += one_hot.scatter(1, action_index.unsqueeze(1), 1)
                mean /= len(map[d_id]['Counterparts'])
            batch['lma'] = th.cat([th.zeros((1, mean.shape[-1])).to(device), mean], dim=0)

            return True, batch
        else:
            return False, None


    def add_reward(self, delta_reward):
        for device in self.current.keys():
            self.current[device]["reward"][-1] += delta_reward

    def save_memory(self,index):
        id_list = []
        m = self.buffer[index]
        with open(self.path + str(index) +'_data.csv', 'w') as f:
            writer = csv.writer(f)
            for id in m.keys():
                writer.writerows(m[id]["obs"])
                writer.writerows(m[id]["immediately_obs"])
                writer.writerows(m[id]["available_action"])
                writer.writerows(m[id]["action"])
                writer.writerows(m[id]["action_index"])
                writer.writerows(m[id]["reward"])
                id_list.append(id)
        with open(self.path + str(index) +'_id.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(id_list)
        return


