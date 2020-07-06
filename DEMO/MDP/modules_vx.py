import numpy as np
import copy
import csv


DECISION_INTERVAL = 60



class Material:
    def __init__(self, id: str, type:bool, bom, remain=float('inf')):
        """
        :param id: 物料编号
        remain : 实际余量 中间产品余量初始化为0或定义余量，原材料初始化为np.inf
        remain_refer : 本轮预期产量
        demand : （完成所有订单的）总体需求量
        demand_refer : （本轮）预期消耗量
        """
        self.id = id
        self.type = type
        self.remain = remain
        self.demand = 0
        self.bom = bom

        self.init_remain = remain
        self.init_bom = copy.deepcopy(bom)

    def __str__(self):
        s = 'Material:' + self.id + ' remain ' + str(self.remain) + ' demand ' + str(self.demand)
        return s

    def produce(self, delta: int):
        self.remain += delta

    def consume(self, delta: int):
        if delta > self.remain:
            print("not enough material")
        self.remain -= delta


    def add_demand(self, delta: int):
        self.demand += delta

class Craft:
    def __init__(self, d_id: str, m_id: str, target, changeTime: int, line_id: str):
        """
        :param id:  目标产品IDx设备 （由于同一工艺编号由于设备存在不同产能，因此工艺根据目标产品IDx设备唯一确定）
        :param target: (目标产品，每分钟产量)
        :param source: list (原材料, 每分钟消耗量)
        :param line_id: 连续生产类别
        """
        self.d_id = d_id
        self.m_id = m_id
        self.target_m = target[0]
        self.productivity = target[1]
        self.source = {o_id:list(self.target_m[o_id].bom) for o_id in self.target_m.keys()}
        self.changeTime = changeTime
        self.line_id = line_id

    def reset(self):
        self.source = {o_id:list(self.target_m[o_id].bom) for o_id in self.target_m.keys()}

    def __str__(self):
        # s = 'Craft of ' + self.d_id + ' productivity:' + str(self.productivity) + ' changeTime:' + str(self.changeTime)
        # s += 'produce:' + str(self.target_m.keys()) + '\n'

        s = 'Craft of ' + self.d_id + ' produce ' + str(self.productivity) + ' ' + str(self.target_m.keys()) + ' by \n \t' \
            + ';'.join([o_id + ':' + self.source[o_id][0][0] + ' ' + str(self.source[o_id][0][1])   for o_id in self.source])
        return s

    def available_actions(self, materials, state, k):
        avail_actions = []
        for o_id in self.source.keys():
            if materials[self.m_id][o_id].demand > materials[self.m_id][o_id].remain:
                flag = 1
                required_production_time = (materials[self.m_id][o_id].demand / k) / self.productivity
                for s, com in self.source[o_id]:
                    if type(materials[s]) == dict:
                        source = materials[s][o_id]
                    else:
                        source = materials[s]
                    # if required_production_time * com * self.productivity > source.remain:
                    if com * self.productivity * required_production_time > source.remain:
                        flag = 0
                        break
                if flag == 1:
                    avail_actions.append([self.m_id, o_id, required_production_time])
        return avail_actions

    def get_state(self, time, materials):
        """
        :param time: 可运行时间
        :return: （real_productivity, refer_productivity）
        """
        ret = {}
        for o_id in self.source.keys():
            for s, com in self.source[o_id]:
                if type(materials[s]) == dict:
                    source = materials[s][o_id]
                else:
                    source = materials[s]
                real_com = com * self.productivity
                if real_com * time > source.remain:
                    ret[o_id] = (self.productivity * DECISION_INTERVAL, 0, 0)
                    break
                ret[o_id] = ([self.productivity * DECISION_INTERVAL, self.productivity * time, 1])
        return ret

    def produce(self, o_id, time, materials):
        target = self.target_m[o_id]
        target.produce(time * self.productivity)

        for s_id, com in self.source[o_id]:
            if type(materials[s_id]) == dict:
                source = materials[s_id][o_id]
            else:
                source = materials[s_id]
            source.consume(time * com * self.productivity)
        return time * self.productivity

    # def act(self, action, time, time_step, materials, std_out_type):
    #     if std_out_type['matrial']:
    #         print(self.d_id, 'act', self.m_id, action['o_id'])
    #     target= self.target_m[action['o_id']]
    #     target.produce(time * self.productivity, self.d_id, time_step, std_out_type)
    #
    #     for s_id, com in self.source[action['o_id']]:
    #         if type(materials[s_id]) == dict:
    #             source = materials[s_id][action['o_id']]
    #         else:
    #             source = materials[s_id]
    #         source.consume(time * com * self.productivity, self.d_id, time_step, std_out_type)
    #         source.add_demand_refer(time * com * self.productivity)
    #     return time * self.productivity
    #
    # def order_act(self, time_step, materials, std_out_type):
    #     flag = True
    #     for o_id in self.target_m.keys():
    #         for index, s in enumerate(self.source[o_id]):
    #             if s[1] > 0:
    #                 if type(materials[s[0]])==dict:
    #                     source = materials[s[0]][o_id]
    #                 else:
    #                     source = materials[s[0]]
    #                 consume = min(s[1], source.remain)
    #
    #                 source.consume(consume, self.d_id, time_step, std_out_type)
    #                 self.source[o_id][index][1] -= consume
    #                 source.add_demand_refer(consume)
    #                 if self.source[o_id][index][1] > 0:
    #                     flag = False
    #                     source.add_demand(self.source[o_id][index][1])
    #     return flag
    #
    #
    # def remain_order_demand(self):
    #     ret = 0
    #     for o_id in self.target_m.keys():
    #         for index, s in enumerate(self.source[o_id]):
    #             ret += s[1]
    #     return ret

class Device:
    """
    get_state
    get_reward
    act
    """
    def __init__(self, id, crafts, operatingHours = [1,1,1]):
        """
        :param id: 设备编号
        :param crafts: 设备可执行工艺 --> 工艺产品：工艺  [Craft] or {m_id: Craft}
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
        self.present_craft = 'wait'
        self.last_craft = 'wait'
        self.record = []

        self.operatingHours = operatingHours
        self.remainChangeTime = 0
        self.accumulateWaitTime = 0
        self.changeCraft = 0
        self.production = {}
        for m_id in self.crafts.keys():
            for o_id in self.crafts[m_id].target_m:
                self.production[m_id + o_id] = 0

    def __str__(self):
        s = '-----Device ID:' + self.id + '-----\n'
        s += 'current action ' + str(self.present_craft) + '\n'
        s += 'have produced:' + str([key +':' + str(self.production[key]) for key in self.production.keys()]) + '\n'
        s += 'have waited:' + str(self.accumulateWaitTime)
        s += '\thave changed:' + str(self.changeCraft)
        return s

    def available_actions(self, materials, state, k):
        avail_actions = []
        for m_id, m_craft in self.crafts.items():
            avail_actions.extend(m_craft.available_actions(materials, state, k))
        return avail_actions
    #
    # def get_state(self, action_to_index, clock: int, materials):
    #     """
    #     :param material_indexs: 本阶段产品
    #     :param clock: 时钟 0，1，2（早晚夜）
    #     :return: state， available
    #     """
    #     state = np.zeros((2,len(action_to_index)-1))
    #     avail_action = np.zeros(len(action_to_index))
    #     avail_action[len(action_to_index)-1] = 1
    #
    #     Ctime = 0
    #     if self.present_craft == 'onChange':
    #         Ctime = min(self.remainChangeTime, DECISION_INTERVAL)
    #         self.remainChangeTime = max(0, self.remainChangeTime - DECISION_INTERVAL)
    #
    #     for m_id in self.crafts.keys():
    #         if self.present_craft == 'onChange':
    #             time = DECISION_INTERVAL - Ctime
    #         else:
    #             if (self.present_craft == m_id) or ((self.present_craft == 'wait') and (self.last_craft in ('wait', m_id))):
    #                 time = DECISION_INTERVAL
    #             else:
    #                 changeTime = self.crafts[self.last_craft].changeTime if self.present_craft == 'wait' else self.crafts[self.present_craft].changeTime
    #                 time = max(0, DECISION_INTERVAL - changeTime)
    #         craft_state = self.crafts[m_id].get_state(time, materials)
    #         for o_id in craft_state:
    #             index = action_to_index[m_id+o_id]
    #             state[0, index] = craft_state[o_id][0]
    #             state[1, index] = craft_state[o_id][1]
    #             avail_action[index] = craft_state[o_id][2]
    #
    #
    #     if not self.operatingHours[clock] or Ctime==DECISION_INTERVAL:
    #         state[1,:] = 0
    #         avail_action = np.zeros(len(action_to_index))
    #
    #     avail_action[len(action_to_index) - 1] = 1
    #     return state.reshape(-1), avail_action


class Stage:
    def __init__(self, name, materials: [Material], devices=None):
        """
        :param name: 流程名
        :param devices:
        :param materials:
        :param refer_crafts:
        """
        self.name=name
        self.materials = materials
        self.devices = devices
        self.index_to_action = []
        self.action_to_index = {}

        count = 0
        for m_id in materials.keys():
            for o_id in materials[m_id].keys():
                ita = {
                    'm_id': m_id,
                    'o_id': o_id
                }
                self.index_to_action.append(ita)
                self.action_to_index[m_id+o_id] = count
                count += 1
        ita = {
            'm_id': 'wait',
            'o_id': ''
        }
        self.index_to_action.append(ita)
        self.action_to_index['wait'] = count


    def __str__(self):
        s = '-----Stage Name:' + self.name + '-----\n'
        s += 'Stage action:' + str([x for x in self.action_to_index.keys()]) + '\n'
        s += 'Stage device:' + str([d.id for d in self.devices]) + '\n'
        return s

    def set_demand(self, materials):
        for action in self.index_to_action[:-1]:
            m = self.materials[action['m_id']][action['o_id']]
            for s, c in m.bom:
                if type(materials[s]) == dict:
                    source = materials[s][action['o_id']]
                else:
                    source = materials[s]
                source.add_demand(c * m.demand)

    def get_state(self):
        state = np.zeros((2,len(self.index_to_action)-1))
        for index, action in enumerate(self.index_to_action[:-1]):
            m = self.materials[action['m_id']][action['o_id']]
            state[0,index], state[1,index] = m.state()
        return state.reshape(-1)

    def info(self):
        env_info = {
            'obs_shape': (len(self.index_to_action)-1)*4,
            'n_actions': len(self.index_to_action),
            'n_agents': len(self.devices)
        }
        return env_info














