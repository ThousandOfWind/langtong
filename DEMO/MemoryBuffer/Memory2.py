import csv
import random
import copy
import numpy as np
import torch as th

class MemoryBuffer:
    def __init__(self, param_set):
        self.buffer = np.array([])
        self.current = {}
        self.mamory_size = param_set['mamory_size']
        self.path = 'data/' + param_set['path']


    def end_trajectory(self):
        np.append(self.buffer,self.current)
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
            np.append(self.current[experience['id']]["obs"],experience["obs"])
            np.append(self.current[experience['id']]["immediately_obs"],experience["immediately_obs"])
            np.append(self.current[experience['id']]["available_action"],experience["available_action"])
            # self.current[experience['id']]["action"].append(experience["action"])
            np.append(self.current[experience['id']]["action_index"],experience["action_index"])
            np.append(self.current[experience['id']]["reward"],experience["reward"])

        else:
            self.current[experience['id']] = {
                "obs": np.array([experience["obs"]]),
                "immediately_obs": np.array([experience["immediately_obs"]]),
                "available_action": np.array([experience['available_action']]),
                # "action": [experience['action']],
                "action_index": np.array([experience['action_index']]),
                "reward": np.array([experience['reward']])
            }

    def sample(self, idList:[], batchSize:int, mf=False, map=None):
        batch ={
            'obs': np.array([]),
            'action': np.array([]),
            'reward': np.array([]),
            'done':np.array([]),
            'next_obs': np.array([]),
            'next_avail_action': np.array([]),
            'last_iobs': np.array([]),
            'iobs': np.array([]),
            #'mean_action': np.array([]),
            #'last_mean_action': np.array([]),
            'bs': batchSize,
        }

        action = {d_id:{} for d_id in idList}


        for item in range(batchSize):
            b_id = random.randint(0, len(self.buffer)-1)
            for d_id in idList:
                np.append(batch['obs'] ,copy.deepcopy(self.buffer[b_id][d_id]['obs']))
                np.append(batch['reward'] , copy.deepcopy(self.buffer[b_id][d_id]['reward']))
                np.append(batch['action'] ,copy.deepcopy(self.buffer[b_id][d_id]['action_index']))
                np.append(batch['done'] , np.array([0,]*(len(self.buffer[b_id][d_id]['action_index'])-1)+[1,]))
                next = copy.deepcopy(self.buffer[b_id][d_id]['obs'][1:])
                np.append(next,np.array([0]* len(self.buffer[b_id][d_id]['obs'][0])))
                np.append(batch['next_obs'], next)
                next_avail = copy.deepcopy(self.buffer[b_id][d_id]['available_action'][1:])
                np.append(next_avail,np.array([0]* len(self.buffer[b_id][d_id]['available_action'][0])))
                np.append(batch['next_avail_action'] , (next_avail))

                np.append(batch['iobs'] , copy.deepcopy(self.buffer[b_id][d_id]['immediately_obs']))
                last_iobs = np.append(self.buffer[b_id][d_id]['immediately_obs'][0:1] , self.buffer[b_id][d_id]['immediately_obs'][:-1])
                np.append(batch['last_iobs'] ,copy.deepcopy(last_iobs))

                if mf:
                    device = th.device("cuda" if th.cuda.is_available() else "cpu")
                    one_hot = th.zeros((len(self.buffer[b_id][d_id]['action_index']), len(self.buffer[b_id][d_id]['available_action'][0]))).to(device)
                    action_index = th.LongTensor(self.buffer[b_id][d_id]['action_index']).to(device)
                    action[d_id][item] = one_hot.scatter(1, action_index.unsqueeze(1), 1)
        return batch
#         '''if mf:
#             for d_id in idList:
#                 for item in range(batchSize):
#                     mean_action = th.zeros_like(action[d_id][item])
#                     for nei in map[d_id]['Counterparts']:
#                         # print(mean_action.shape, action[nei][item].shape)
#                         mean_action += action[nei][item]
#                     mean_action /= len(map[d_id]['Counterparts'])
#
#                     batch['mean_action'].append(copy.deepcopy(mean_action))
#                     batch['last_mean_action'].append(th.zeros((1, mean_action.shape[-1])).to(device))
#                     batch['last_mean_action'].append(copy.deepcopy(mean_action[:-1]))
#             batch['mean_action'] = th.cat(batch['mean_action'], dim=0).to(device)
#             batch['last_mean_action'] = th.cat(batch['last_mean_action'], dim=0).to(device)
# '''

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

    def add_reward(self, delta_reward):
        for device in self.current.keys():
           self.current[device]["reward"][-1] += delta_reward

    def save_memory(self,index):
        id_list = np.array([])
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


