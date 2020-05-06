import numpy as np
from .reward import REWARD_RUlE

DECISION_INTERVAL = 30
REWARD_Function = REWARD_RUlE


class Material:
    def __init__(self, id: str, remain=float('inf')):
        """
        :param id: 物料编号
        remain : 实际余量 中间产品余量初始化为0或定义余量，原材料初始化为np.inf
        remain_refer : 本轮预期产量
        demand : （完成所有订单的）总体需求量
        demand_refer : （本轮）预期消耗量
        """
        self.id = id
        self.remain = remain
        self.product_refer = 0
        self.demand = 0
        self.demand_refer = 0
        self.record = []

    def __str__(self):
        s = 'Material ' + self.id + ' remain ' + str(self.remain) + ' demand ' + str(self.demand)
        return s

    def add_remain(self, delta: int, id, ts):
        self.remain += delta
        self.product_refer += delta
        self.record.append((ts, id, delta))


    def add_demand(self, delta: int):
        self.demand += delta

    def add_demand_refer(self, delta: int):
        self.demand_refer += delta

    def clear(self):
        self.demand = self.demand_refer = self.product_refer = 0

    def state(self):
        return [self.demand-self.remain, self.demand_refer-self.product_refer]

class Craft:
    def __init__(self, id: str, target: (Material, int), source: [(Material, int),], changeTime: int):
        """
        :param id:  目标产品IDx设备 （由于同一工艺编号由于设备存在不同产能，因此工艺根据目标产品IDx设备唯一确定）
        :param target: (目标产品，每分钟产量)
        :param source: list (原材料, 每分钟消耗量)
        """
        self.id = id
        self.target = target
        self.source = source
        self.changeTime = changeTime

    def __str__(self):
        s = '-----Craft ID:' + self.id + '-----\n'
        s += 'produce:' + self.target[0].id + ':' + str(self.target[1]) + '\n'
        s += 'consume:' + str([d[0].id + ':' + str(d[1]) for d in self.source]) + '\n'
        s += 'changeTime:' + str(self.changeTime)
        return s

    def get_cv(self):
        return self.target[0], [(s[0], s[1]/self.target[1]) for s in self.source]

    def state(self, time):
        """
        :param time: 可运行时间
        :return: （real_productivity, refer_productivity）
        """
        for matrial, com in self.source:
            if com * time > matrial.remain:
                return (self.target[1] * DECISION_INTERVAL, 0)
        return  (self.target[1] * DECISION_INTERVAL, time * self.target[1])

    def act(self, time, time_step):
        target, p = self.target
        target.add_remain(time * p, self.id, time_step)
        for matrial, com in self.source:
            matrial.add_remain(-time * com, self.id, time_step)
            matrial.add_demand_refer(time * com)
        return time * p

    def order_act(self, targetP, sum_req, sum_real, time_step):
        flag = True
        for index, s in enumerate(self.source):
            if s[1] > 0:
                p_id = targetP[s[0].id]
                consume = min(s[1], (s[1]/sum_req[p_id])*sum_real)

                s[0].add_remain(-consume, self.id, time_step)
                self.source[index][1] -= consume
                s[0].add_demand_refer(consume)
                if self.source[index][1] <= 0:
                    flag = False
        return flag

class Device:
    """
    get_state
    get_reward
    act
    """
    def __init__(self, id, crafts: [Craft], operatingHours = [1,1,1]):
        """
        :param id: 设备编号
        :param crafts: 设备可执行工艺 --> 工艺产品：工艺
        :param operatingHours: 一天有三个班次，若该班次可执行用1表示
        present_craft: 当前在执行工艺, None, 'onchange'
        state: <real_productivity>, <refer_productivity>,
        """
        self.id = id
        if type(crafts) == list:
            self.crafts = {}
            for craft in crafts:
                self.crafts[craft.target[0].id] = craft
        else:
            self.crafts = crafts
        self.operatingHours = operatingHours
        self.remainChangeTime = 0
        self.reward = 0
        self.accumulateReward = 0
        self.accumulateWaitTime = 0
        self.changeCraft = 0
        self.production = {}
        for craft in self.crafts.keys():
            self.production[craft] = 0

    def __str__(self):
        s = '-----Device ID:' + self.id + '-----\n'
        s += 'current action ' + str(self.present_craft) + '\n'
        s += 'total reward ' + str(self.accumulateReward) + '\n'
        s += 'have produced:' + str([d +':' + str(self.production[d]) for d in self.crafts]) + '\n'
        s += 'have waited:' + str(self.accumulateWaitTime)
        s += '\thave changed:' + str(self.changeCraft)
        return s

    def reset(self):
        self.present_craft = 'wait'
        self.last_craft = 'wait'
        self.remainChangeTime = 0
        self.reward = 0
        self.accumulateReward = 0
        self.accumulateWaitTime = 0
        self.record = []
        self.changeCraft = 0
        self.production = {}
        for craft in self.crafts.keys():
            self.production[craft] = 0

    def get_state(self, material_indexs: [str], clock: int):
        """
        :param material_indexs: 本阶段产品
        :param clock: 时钟 0，1，2（早晚夜）
        :return: state， available
        """
        avail_action = np.zeros(len(material_indexs)+1)
        state = np.zeros((2,len(material_indexs)))
        avail_action[len(material_indexs)] = 1

        if self.operatingHours[clock]:
            if self.present_craft == 'onChange':
                changeTime = min(self.remainChangeTime, DECISION_INTERVAL)
                self.remainChangeTime = max(0, self.remainChangeTime - DECISION_INTERVAL)
            elif self.present_craft != 'wait':
                changeTime = self.crafts[self.present_craft].changeTime
            else:
                changeTime = 0

            time = max(0, DECISION_INTERVAL-changeTime)
            self.remainChangeTime = max(changeTime-DECISION_INTERVAL, 0)

            for i, product in enumerate(material_indexs):
                if product in self.crafts.keys():
                    if product == self.present_craft:
                        craft_state = self.crafts[product].state(time=DECISION_INTERVAL)
                    else:
                        craft_state = self.crafts[product].state(time=time)
                    state[0,i] = craft_state[0]
                    state[1,i] = craft_state[1]
                    avail_action[i] = 1 if craft_state[1] > 0 else 0

        return state.reshape(-1), avail_action

    def get_reward(self):
        return self.reward

    def order_act(self, targetP, M, time_step):
        requirMatrix = np.zeros((len(self.crafts), len(targetP)))
        for index,c in enumerate(self.crafts.keys()):
            for s, r in self.crafts[c].source:
                requirMatrix[targetP[index, s.id]] = r

        sum_req = requirMatrix.sum(axis=0)
        sum_real = np.array([M[source].remain] for source in targetP.keys())

        ret = True
        for c in self.crafts.keys():
            ret = ret and self.crafts[c].order_act(targetP, sum_req, sum_real, time_step)
        return ret

    def order_demand(self):
        for index,c in enumerate(self.crafts.keys()):
            for s, r in self.crafts[c].source:
                s.add_demand(r)

    def remain_order_demand(self):
        ret = 0
        for index,c in enumerate(self.crafts.keys()):
            for s, r in self.crafts[c].source:
                ret + r
        return ret

    def act(self, action, time_step):
        """
        :param action:
        :return: wait_time if change_craft
        """
        self.accumulateReward += self.reward
        self.reward = 0
        if action == 'wait':
            self.last_craft = self.present_craft
            self.present_craft = 'wait'
            self.remainChangeTime = max(0, self.remainChangeTime - DECISION_INTERVAL)
            self.accumulateWaitTime += DECISION_INTERVAL
            self.record.append((time_step,'wait'))
            return

        if self.present_craft == 'onChange':
            if self.remainChangeTime >= DECISION_INTERVAL:
                self.remainChangeTime -= DECISION_INTERVAL
                self.reward += REWARD_Function['wait'] * DECISION_INTERVAL
                self.record.append((time_step, 'change'))
                return
            else:
                time = DECISION_INTERVAL - self.remainChangeTime
                wait = self.remainChangeTime
                self.accumulateWaitTime += wait
                self.remainChangeTime = 0
                self.present_craft = action

        elif self.present_craft == action or (self.present_craft=='wait' and self.last_craft in ('wait', action)):
            time = DECISION_INTERVAL

        else:
            self.record.append((time_step, 'change'))
            self.last_craft = 'wait'
            changeTime = self.crafts[self.present_craft].changeTime
            self.changeCraft += 1

            if changeTime > DECISION_INTERVAL:
                self.present_craft = 'onChange'
                self.remainChangeTime = changeTime - DECISION_INTERVAL
                self.reward += REWARD_Function['wait']
                self.accumulateWaitTime += DECISION_INTERVAL
                return
            else:
                self.present_craft = action
                time = DECISION_INTERVAL - changeTime
                self.accumulateWaitTime += changeTime
        self.record.append((time_step, action))
        productivity =  self.crafts[action].act(time, time_step)
        self.production[action] += productivity

        # self.reward += REWARD_Function[action] * productivity
        return

class Stage:
    def __init__(self, name, materials: [Material]):
        """
        :param name: 流程名
        :param devices:
        :param materials:
        :param refer_crafts:
        """
        self.name=name
        self.materials = materials
        self.material_indexes = [m.id for m in materials]
        self.refer_c = {}
        self.devices = []

    def __str__(self):
        s = '-----Stage Name:' + self.name + '-----\n'
        s += 'Stage production:' + str(self.material_indexes) + '\n'
        s += 'Stage device:' + str([d.id for d in self.devices]) + '\n'
        return s

    def set_devices(self, devices: [Device]):
        self.devices = devices
        for m in self.material_indexes:
            for d in self.devices:
                if m in d.crafts.keys():
                    self.refer_c[m] = d.crafts.keys()[m]
                    break

    def set_demand(self):
        for c in self.refer_c:
            tm, source = self.refer_c[c].get_cv()
            tm_demand = tm.demand
            for s, q in source:
                s.add_demand(q * tm_demand)


    def get_state(self):
        state = np.zeros((2,len(self.materials)))
        for i, m in enumerate(self.materials):
            state[0,i], state[1,i] = m.state()
        return state.reshape(-1)

    def indexToAction(self, action_index):
        if action_index== len(self.material_indexes):
            action = 'wait'
        else:
            action = self.material_indexes[action_index]
        return action


    def step(self, agents, memoryBuffer, clock, t):
        """
        :param agents:
        :return:
        """
        for device in self.devices:
            stage_state = self.get_state()
            device_state, available_action = device.get_state(material_indexs=self.material_indexes, clock=clock)
            state = np.concatenate([stage_state, device_state])
            action_index = agents.choose_action(state = state, available_action=available_action, t=t, id= device.id)
            action = self.indexToAction(action_index)
            device.act(action)
            reward = device.get_reward() # 可补充其他奖赏逻辑

            experience = {
                "id": device.id,
                "step": t,
                "state": state,
                "available_action": available_action,
                "action": action,
                "action_index": action_index,
                "reward": reward
            }
            memoryBuffer.append(experience)
        self.set_demand()


    def info(self):
        env_info = {
            'state_len': len(self.materials)*4,
            'num_actions': len(self.materials)+1,
            'num_agents': len(self.devices)
        }
        return env_info














