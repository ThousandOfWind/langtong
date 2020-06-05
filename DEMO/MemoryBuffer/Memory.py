import csv
import random

class MemoryBuffer:
    def __init__(self, param_set):
        self.buffer = []
        self.current = {}
        self.mamory_size = param_set['mamory_size']
        self.path = 'data/' + param_set['path']

    def end_trajectory(self):
        self.buffer.append(self.current)
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
            self.current[experience['id']]["action"].append(experience["action"])
            self.current[experience['id']]["action_index"].append(experience["action_index"])
            self.current[experience['id']]["reward"].append(experience["reward"])

        else:
            self.current[experience['id']] = {
                "obs": [experience["obs"]],
                "immediately_obs": [experience["immediately_obs"]],
                "available_action": [experience['available_action']],
                "action": [experience['action']],
                "action_index": [experience['action_index']],
                "reward": [experience['reward']]
            }

    def sample(self, idList:[], batchSize:int):
        batch ={
            'obs': [],
            'action': [],
            'reward': [],
            'done':[],
            'next_obs': [],
            'next_avail_action': []
        }
        for d_id in idList:
            for item in range(batchSize):
                b_id = random.randint(0, len(self.buffer)-1)
                step = random.randint(0, len(self.buffer[b_id][d_id]['obs'])-1)
                batch['obs'].append(self.buffer[b_id][d_id]['obs'][step])
                batch['reward'].append(self.buffer[b_id][d_id]['reward'][step])
                batch['action'].append(self.buffer[b_id][d_id]['action_index'][step])
                if step == len(self.buffer[b_id][d_id]['obs'])-1:
                    batch['done'].append(1)
                    batch['next_obs'].append([0]* len(self.buffer[b_id][d_id]['obs'][step]))
                    batch['next_avail_action'].append([1]* len(self.buffer[b_id][d_id]['available_action'][step]))
                else:
                    batch['done'].append(0)
                    batch['next_obs'].append(self.buffer[b_id][d_id]['obs'][step+1])
                    batch['next_avail_action'].append(self.buffer[b_id][d_id]['available_action'][step+1])
        return batch


    def add_reward(self, delta_reward):
        for device in self.current.keys():
            self.current[device]["reward"][-1] += delta_reward

    def save_memory(self,index):
        id_list = []
        m = self.buffer[index]
        with open(self.path + str(index) +'_data.csv', 'w') as f:
            writer = csv.writer(f)
            for id in m.keys():
                writer.writerows(m[id]["state"])
                writer.writerows(m[id]["available_action"])
                writer.writerows(m[id]["action"])
                writer.writerows(m[id]["action_index"])
                writer.writerows(m[id]["reward"])
                id_list.append(id)
        with open(self.path + str(index) +'_id.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(id_list)
        return


