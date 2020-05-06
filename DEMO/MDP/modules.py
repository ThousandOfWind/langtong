import numpy as np
from .reward import REWARD_RUlE

DECISION_INTERVAL = 30
REWARD_Function = REWARD_RUlE


class Material:
    def __init__(self, id: str, remain=np.inf):
        """
        :param id: 物料编号
        remain : 实际余量 中间产品余量初始化为0或定义余量，原材料初始化为np.inf
        remain_refer : 本轮预期产量
        demand : （完成所有订单的）总体需求量
        demand_refer : （本轮）预期消耗量
        """
        self.id = id
        self.remain = remain
        self.remain_refer = 0
        self.demand = 0
        self.demand_refer = 0

    def add_remain_refer(self, delta: int):
        self.demand_refer += delta

    def add_demand(self, delta: int):
        self.demand += delta

    def add_demand_refer(self, delta: int):
        self.demand_refer += delta

    def clear_demand(self):
        self.demand = self.demand_refer = 0

    def step(self):
        self.remain = self.remain + self.remain_refer - self.demand_refer
        self.remain_refer = self.demand_refer = 0

    def state(self):
        return [self.demand-self.remain, self.demand_refer-self.remain_refer]

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

    def state(self, time):
        """
        :param time: 可运行时间
        :return: （real_productivity, refer_productivity）
        """
        for matrial, com in self.source:
            if com * time > matrial.remain:
                return (self.target[1] * DECISION_INTERVAL, 0)
        return  (self.target[1] * DECISION_INTERVAL, time * self.target[1])

    def action(self, time):
        target, p = self.target
        target.add_remain_refer(time * p)
        for matrial, com in self.source:
            matrial.add_demand_refer(time * com)
        return time * p

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
        self.crafts = {}
        for craft in crafts:
            self.crafts[craft.target[0].id] = craft
        self.present_craft = None
        self.operatingHours = operatingHours
        self.remainChangeTime = 0
        self.last_reward = 0

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
            elif self.present_craft != None:
                changeTime = self.crafts[self.present_craft].changeTime

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
        return self.last_reward

    def act(self, action):
        if self.present_craft == 'onChange':
            if self.remainChangeTime >= DECISION_INTERVAL:
                self.remainChangeTime -= DECISION_INTERVAL
                self.last_reward = REWARD_Function['wait']
                return
            else:
                time = DECISION_INTERVAL - self.remainChangeTime
                self.remainChangeTime = 0

        elif self.present_craft == action:
            time = DECISION_INTERVAL
        else:
            changeTime = self.crafts[self.present_craft].changeTime
            if changeTime > DECISION_INTERVAL:
                self.present_craft = 'onChange'
                self.remainChangeTime = changeTime - DECISION_INTERVAL
                self.last_reward = REWARD_Function['wait']
                return
            else:
                time = DECISION_INTERVAL - changeTime
        productivity =  self.crafts[action].act(action, time)
        self.last_reward = REWARD_Function[action] * productivity

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

    def set_devices(self, devices: [Device]):
        self.devices = devices


    def state(self):
        state = np.zeros((2,len(self.materials)))
        for i, m in enumerate(self.materials):
            state[0,i], state[1,i] = m.state()
        return state.shape(-1)


    def step(self, agents):
        """
        :param agents:
        :return:
        """
        for device, agent in zip(self.devices, agents):
            stage_state = self.state()
            device_state, available_action = device.get_state()
            state = np.cat([stage_state, device_state])
            action = agent.choose_action(state = state, available_action=available_action)
            device.act(action)
            reward = device.get_reward() # 可补充其他奖赏逻辑
            agent.learn(state = state, available_action=available_action, action=action, reward=reward)

    def info(self):
        env_info = {
            'inputSize': len(self.materials)*4,
            'num_actions': len(self.materials)+1,
            'num_agents': len(self.devices)
        }
        return env_info














