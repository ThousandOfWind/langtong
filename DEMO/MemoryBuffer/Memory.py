import csv

class MemoryBuffer:
    def __init__(self):
        self.buffer = []
        self.current = {}
        self.path = 'data/memory/0/'

    def new_memory(self):
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
            self.current[experience['id']]["state"].append(experience["state"])
            self.current[experience['id']]["available_action"].append(experience["available_action"])
            self.current[experience['id']]["action"].append(experience["action"])
            self.current[experience['id']]["action_index"].append(experience["action_index"])
            self.current[experience['id']]["reward"].append(experience["reward"])

        else:
            self.current[experience['id']] = {
                "state": [experience["state"]],
                "available_action": [experience['available_action']],
                "action": [experience['action']],
                "action_index": [experience['action_index']],
                "reward": [experience['reward']]
            }

    def get_batch(self, idList:[], batchSize:int):
        return

    def get_current(self, idList:[]):
        return

    def add_reward(self, delta_reward):
        for device in self.current.keys():
            self.current[device]["reward"] += delta_reward



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


