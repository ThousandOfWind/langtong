import numpy as np
import copy
import csv


DECISION_INTERVAL = 60

def set_demand(m_id, o_id, quantity, materials):
    mat = materials[m_id][o_id]
    mat.add_demand(quantity)
    # print(o_id, m_id, quantity, mat.demand, mat.state())

    for s, c in mat.bom:
        if type(materials[s]) == dict:
            set_demand(s, o_id, quantity * c, materials)
        else:
            materials[s].add_demand(c * quantity)
    return

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
        self.product_refer = 0
        self.demand = 0
        self.demand_refer = 0
        self.last_demand_refer = 0
        self.record = []
        self.bom = bom
        self.bottom = None

        self.init_remain = remain
        self.init_bom = copy.deepcopy(bom)


    def reset(self):
        self.product_refer = 0
        self.demand = 0
        self.demand_refer = 0
        self.last_demand_refer = 0
        self.record = []

        self.remain = self.init_remain
        self.bom = copy.deepcopy(self.init_bom)


    def __str__(self):
        s = 'Material:' + self.id + ' remain ' + str(self.remain) + ' demand ' + str(self.demand) \
            + ' this step produce ' + str(self.product_refer) + ' last step conmsume ' + str(self.last_demand_refer)
        return s

    def produce(self, delta: int, id, ts, std_out_type):
        if std_out_type['matrial']:
            print('\t', 'produce from', str(self))

        self.product_refer += delta

        if std_out_type['matrial']:
            print('\t', '\t to', str(self))
        self.record.append((ts, id, delta))

    def consume(self, delta: int, id, ts, std_out_type):
        if std_out_type['matrial']:
            print('\t', 'consume from', str(self))

        # 忽略由于浮点数导致的问题
        if delta > self.remain:
            delta = self.remain
        #     print(ts, id, -delta, str(self))

        self.remain -= delta

        if std_out_type['matrial']:
            print('\t', '\t to', str(self))

        self.record.append((ts, id, -delta))


    def add_demand(self, delta: int):
        self.demand += delta

    def add_demand_refer(self, delta: int):
        self.demand_refer += delta

    def clear(self):
        self.remain += self.product_refer
        self.last_demand_refer = self.demand_refer
        self.demand = self.demand_refer = self.product_refer = 0

    def state(self):
        real = self.demand - self.remain - self.product_refer
        # if not self.bottom is None and self.demand > 0:
        #     real = max(self.bottom[0], real)
        refer = self.last_demand_refer - self.product_refer
        return [real, refer]

class Craft:
    def __init__(self, d_id: str, m_id: str, target, changeTime: int):
        """
        :param id:  目标产品IDx设备 （由于同一工艺编号由于设备存在不同产能，因此工艺根据目标产品IDx设备唯一确定）
        :param target: (目标产品，每分钟产量)
        :param source: list (原材料, 每分钟消耗量)
        """
        self.d_id = d_id
        self.m_id = m_id
        self.target_m = target[0]
        self.productivity = target[1]
        self.source = {o_id:list(self.target_m[o_id].bom) for o_id in self.target_m.keys()}
        self.changeTime = changeTime

    def reset(self):
        self.source = {o_id:list(self.target_m[o_id].bom) for o_id in self.target_m.keys()}

    def __str__(self):
        # s = 'Craft of ' + self.d_id + ' productivity:' + str(self.productivity) + ' changeTime:' + str(self.changeTime)
        # s += 'produce:' + str(self.target_m.keys()) + '\n'

        s = 'Craft of ' + self.d_id + ' produce ' + str(self.productivity) + ' ' + str(self.target_m.keys()) + ' by \n \t' \
            + ';'.join([o_id + ':' + self.source[o_id][0][0] + ' ' + str(self.source[o_id][0][1])   for o_id in self.source])
        return s

    def get_state(self, time, materials):
        """
        :param time: 可运行时间
        :return: （real_productivity, refer_productivity）
        """
        ret = {}
        for o_id in self.source.keys():
            t = float('inf')
            for s, com in self.source[o_id]:
                if type(materials[s]) == dict:
                    source = materials[s][o_id]
                else:
                    source = materials[s]

                t = min(t, source.remain / (self.productivity * com))
                # real_com = com * self.productivity
                # if real_com * time > source.remain:
                #     ret[o_id] = (self.productivity * DECISION_INTERVAL, 0, 0)
                #     break

            if t >= time:
                ret[o_id] = ([self.productivity * DECISION_INTERVAL, self.productivity * time, 1])
            elif self.productivity * t > materials[self.m_id][o_id].state()[0] > 0:
                ret[o_id] = ([self.productivity * DECISION_INTERVAL, self.productivity * t, 1])
            else:
                ret[o_id] = (self.productivity * DECISION_INTERVAL, 0, 0)

        return ret



    def act(self, action, time, time_step, materials, std_out_type):
        if std_out_type['matrial']:
            print(self.d_id, 'act', self.m_id, action['o_id'])

        o_id = action['o_id']
        target= self.target_m[o_id]
        target.produce(time * self.productivity, self.d_id, time_step, std_out_type)


        t = time
        for s, com in self.source[o_id]:
            if type(materials[s]) == dict:
                source = materials[s][o_id]
            else:
                source = materials[s]
            t = min(t, source.remain / (self.productivity * com))

        for s_id, com in self.source[o_id]:
            if type(materials[s_id]) == dict:
                source = materials[s_id][o_id]
            else:
                source = materials[s_id]

            source.consume(t * com * self.productivity, self.d_id, time_step, std_out_type)
            source.add_demand_refer(t * com * self.productivity)
        return t * self.productivity

    def order_act(self, time_step, materials, std_out_type):
        flag = True
        for o_id in self.target_m.keys():
            for index, s in enumerate(self.source[o_id]):
                if s[1] > 0:
                    source = materials[s[0]][o_id]
                    consume = min(s[1], source.remain)

                    source.consume(consume, self.d_id, time_step, std_out_type)
                    self.source[o_id][index][1] -= consume

                    if self.source[o_id][index][1] > 0:
                        flag = False
                        if std_out_type['matrial']:
                            print('order', s[0], s[1], source.remain)

                        source.add_demand_refer(consume)
                        set_demand(s[0], o_id, self.source[o_id][index][1], materials)
        return flag


    def remain_order_demand(self):
        ret = 0
        for o_id in self.target_m.keys():
            for index, s in enumerate(self.source[o_id]):
                ret += s[1]
        return ret

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
        self.reward = 0
        self.accumulateReward = 0
        self.accumulateWaitTime = 0
        self.changeCraft = 0
        self.production = {}
        for m_id in self.crafts.keys():
            for o_id in self.crafts[m_id].target_m:
                self.production[m_id + o_id] = 0

    def save(self, path):
        with open(path + str(self.id) + '_history.csv', 'w', newline ='') as f:
            writer = csv.writer(f)
            writer.writerows(self.record)
        return

    def reset(self):
        self.present_craft = 'wait'
        self.last_craft = 'wait'
        self.remainChangeTime = 0
        self.reward = 0
        self.accumulateReward = 0
        self.accumulateWaitTime = 0
        self.changeCraft = 0
        self.record = []
        self.production = {}
        for m_id in self.crafts.keys():
            for o_id in self.crafts[m_id].target_m:
                self.production[m_id + o_id] = 0

    def __str__(self):
        s = '-----Device ID:' + self.id + '-----\n'
        s += 'current action ' + str(self.present_craft) + '\n'
        s += 'total reward ' + str(self.accumulateReward) + '\n'
        s += 'have produced:' + str([key +':' + str(self.production[key]) for key in self.production.keys()]) + '\n'
        s += 'have waited:' + str(self.accumulateWaitTime)
        s += '\thave changed:' + str(self.changeCraft)
        return s

    def get_state(self, action_to_index, clock: int, materials):
        """
        :param material_indexs: 本阶段产品
        :param clock: 时钟 0，1，2（早晚夜）
        :return: state， available
        """
        state = np.zeros((2,len(action_to_index)-1))
        avail_action = np.zeros(len(action_to_index))
        avail_action[len(action_to_index)-1] = 1

        Ctime = 0
        if self.present_craft == 'onChange':
            Ctime = min(self.remainChangeTime, DECISION_INTERVAL)
            self.remainChangeTime = max(0, self.remainChangeTime - DECISION_INTERVAL)

        for m_id in self.crafts.keys():
            if self.present_craft == 'onChange':
                time = DECISION_INTERVAL - Ctime
            else:
                if (self.present_craft == m_id) or ((self.present_craft == 'wait') and (self.last_craft in ('wait', m_id))):
                    time = DECISION_INTERVAL
                else:
                    changeTime = self.crafts[self.last_craft].changeTime if self.present_craft == 'wait' else self.crafts[self.present_craft].changeTime
                    time = max(0, DECISION_INTERVAL - changeTime)
            craft_state = self.crafts[m_id].get_state(time, materials)
            for o_id in craft_state:
                index = action_to_index[m_id+o_id]
                state[0, index] = craft_state[o_id][0]
                state[1, index] = craft_state[o_id][1]
                avail_action[index] = craft_state[o_id][2]


        if not self.operatingHours[clock] or Ctime==DECISION_INTERVAL:
            state[1,:] = 0
            avail_action = np.zeros(len(action_to_index))

        avail_action[len(action_to_index) - 1] = 1
        return state.reshape(-1), avail_action

    def get_reward(self):
        return self.reward

    def add_reward(self, delta):
        self.reward += delta

    def check_action(self, action_to_index, clock: int, materials, action):
        _, avail = self.get_state(action_to_index, clock, materials)
        index = action_to_index[action['m_id'] + action['o_id']]
        print(avail, index, avail[index])

    def act_with_time(self, time, action, time_step, clock, materials, reward_rule, std_out_type):
        """
        :param action:
        :return: wait_time if change_craft
        """
        self.accumulateReward += self.reward
        self.reward = 0
        if not self.operatingHours[clock]:
            self.record.append([time_step, 'close'])
            return

        if action['m_id'] == 'wait':
            self.reward += reward_rule['wait'] * time
            self.last_craft = self.present_craft
            self.present_craft = 'wait'
            self.remainChangeTime = max(0, self.remainChangeTime - time)
            self.accumulateWaitTime += time
            self.record.append([time_step,'wait'])
            return

        # self.check_action(action_to_index, clock, materials, action)


        if self.present_craft == 'onChange':
            if self.remainChangeTime >= time:
                self.remainChangeTime -= time
                self.reward += reward_rule['wait'] * time
                self.record.append([time_step, 'change'])
                return
            else:
                time = time - self.remainChangeTime
                wait = self.remainChangeTime
                self.reward += reward_rule['wait'] * wait
                self.accumulateWaitTime += wait
                self.remainChangeTime = 0
                self.present_craft = action['m_id']

        elif self.present_craft == action['m_id'] or (self.present_craft=='wait' and self.last_craft in ('wait', action['m_id'])):
            time = time


        else:
            print(time_step, self.id, 'Change')
            self.last_craft = 'wait'
            changeTime = self.crafts[self.present_craft].changeTime
            self.changeCraft += 1
            self.reward += reward_rule['changeCraft'] * changeTime
            if changeTime > time:
                self.present_craft = 'onChange'
                self.remainChangeTime = changeTime - time
                self.reward += reward_rule['wait'] * time
                self.accumulateWaitTime += time
                return
            else:
                self.present_craft = action['m_id']
                time = time - changeTime
                self.reward += reward_rule['wait'] * changeTime
                self.accumulateWaitTime += changeTime
        productivity =  self.crafts[action['m_id']].act(action, time, time_step, materials, std_out_type)
        self.production[action['m_id']+ action['o_id']] += productivity
        self.record.append([time_step, action['m_id'], action['o_id'], productivity])


        # self.reward += reward_rule[action] * productivity
        return



    def act(self, action, time_step, clock, materials, reward_rule, std_out_type):
        """
        :param action:
        :return: wait_time if change_craft
        """
        self.accumulateReward += self.reward
        self.reward = 0
        if not self.operatingHours[clock]:
            self.record.append([time_step, 'close'])
            return 0

        if action['m_id'] == 'wait':
            self.reward += reward_rule['wait'] * DECISION_INTERVAL
            self.last_craft = self.present_craft
            self.present_craft = 'wait'
            self.remainChangeTime = max(0, self.remainChangeTime - DECISION_INTERVAL)
            self.accumulateWaitTime += DECISION_INTERVAL
            self.record.append([time_step,'wait'])
            return 0

        # self.check_action(action_to_index, clock, materials, action)


        if self.present_craft == 'onChange':
            if self.remainChangeTime >= DECISION_INTERVAL:
                self.remainChangeTime -= DECISION_INTERVAL
                self.reward += reward_rule['wait'] * DECISION_INTERVAL
                self.record.append([time_step, 'change'])
                return 0
            else:
                time = DECISION_INTERVAL - self.remainChangeTime
                wait = self.remainChangeTime
                self.reward += reward_rule['wait'] * wait
                self.accumulateWaitTime += wait
                self.remainChangeTime = 0
                self.present_craft = action['m_id']

        elif self.present_craft == action['m_id'] or (self.present_craft=='wait' and self.last_craft in ('wait', action['m_id'])):
            time = DECISION_INTERVAL


        else:
            print(time_step, self.id, 'Change')
            self.last_craft = 'wait'
            changeTime = self.crafts[self.present_craft].changeTime
            self.changeCraft += 1
            self.reward += reward_rule['changeCraft'] * changeTime
            if changeTime > DECISION_INTERVAL:
                self.present_craft = 'onChange'
                self.remainChangeTime = changeTime - DECISION_INTERVAL
                self.reward += reward_rule['wait'] * DECISION_INTERVAL
                self.accumulateWaitTime += DECISION_INTERVAL
                return 0
            else:
                self.present_craft = action['m_id']
                time = DECISION_INTERVAL - changeTime
                self.reward += reward_rule['wait'] * changeTime
                self.accumulateWaitTime += changeTime
        productivity =  self.crafts[action['m_id']].act(action, time, time_step, materials, std_out_type)
        self.production[action['m_id']+ action['o_id']] += productivity
        self.record.append([time_step, action['m_id'], action['o_id'], productivity])


        # self.reward += reward_rule[action] * productivity
        return productivity

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
        self.obId = False


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
        need = np.zeros(len(self.index_to_action))
        for index, action in enumerate(self.index_to_action[:-1]):
            m = self.materials[action['m_id']][action['o_id']]
            state[0,index], state[1,index] = m.state()
            need[index] = 1 if state[0,index] > 0 else 0
        return state.reshape(-1), need

    def stage_sequantial_step(self, agents, memoryBuffer, clock, t, materials, std_out_type, reward_rule, e=0):
        """
        :param agents:
        :return:
        """
        for index, device in enumerate(self.devices):
            stage_state, need = self.get_state()
            device_state, available_action = device.get_state(action_to_index=self.action_to_index, clock=clock, materials=materials)
            available_action *= need
            if available_action.sum()==0:
                available_action[-1] = 1
            obs = np.concatenate([stage_state, device_state])
            # print(available_action)


            if self.obId:
                id = [0] * len(self.devices)
                id[index] = 1
                obs = np.concatenate([obs, id])
            action_index = agents.choose_action(obs=obs, available_action=available_action, t=t, d_id=device.id, episode=e, std_out_type=std_out_type, memory=memoryBuffer)
            action = self.index_to_action[action_index]

            productivity = device.act( action, t, clock, materials, reward_rule, std_out_type)
            # print(action_index, action, productivity)


            # 补充其他奖赏逻辑
            device.add_reward(reward_rule['step'])
            if action['m_id'] == 'wait':
                reward = device.get_reward()
            else:
                mnr = reward_rule['meet_need'] if stage_state[action_index]>0 else 0
                device.add_reward(mnr)
                reward = device.get_reward()

            immediately_stage_state, _ = self.get_state()
            immediately_device_state, _ = device.get_state(action_to_index=self.action_to_index, clock=clock, materials=materials)
            immediately_obs = np.concatenate([immediately_stage_state, immediately_device_state])

            if self.obId:
                immediately_obs = np.concatenate([immediately_obs, id])

            experience = {
                "id": device.id,
                "step": t,
                "obs": obs,
                "immediately_obs": immediately_obs,
                "available_action": available_action,
                "action": action,
                "action_index": action_index,
                "reward": reward
            }
            if std_out_type['device_action']:
                print(t, ':', device.id, action['m_id'], action['o_id'], reward)

            memoryBuffer.append(experience)


    def info(self):
        if self.obId:
            env_info = {
                'obs_shape': (len(self.index_to_action) - 1) * 4 + len(self.devices),
                'n_actions': len(self.index_to_action),
                'n_agents': len(self.devices)
            }
            return env_info
        env_info = {
            'obs_shape': (len(self.index_to_action)-1)*4,
            'n_actions': len(self.index_to_action),
            'n_agents': len(self.devices)
        }
        return env_info














