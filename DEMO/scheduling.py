from data.read2 import MATERIAL, DEVICE, DEMAND, get_oder
from data.create_map import Equipment_Relation_Map
import copy
import sys

sys.setrecursionlimit(2000)
k = 1  # 每份订单分成k份



def schedule(states, materials):
    # print(states)
    next_time = float("inf")  # "快进"时间
    flag = 1
    for device, state in states.items():
        if 0 < state[0] < next_time:  # "快进"至最近结束的任务
            next_time = state[0]
        if state[0] == 0:
            flag = 0
    if flag == 1:  # 没有待安排的设备，可快进至 next_time， 并完成对应生产
        for device_id, state in states.items():
            if state[0] > 0:
                state[0] -= next_time
                DEVICE[device_id].crafts[state[1]].produce(state[2], next_time, materials)
            elif state[0] == -1:
                state[3] += next_time
    else:
        next_time = 0

    completed = 1
    for o_id, order in orderML.items():
        if order.bom[0][1] > materials[order.bom[0][0]][o_id].remain:
            completed = 0
    if completed == 1:
        print('complete')
        return next_time, {}

    for m_id in MATERIAL.keys():
        if type(MATERIAL[m_id]) == dict:
            for o_id in MATERIAL[m_id].keys():
                print(MATERIAL[m_id][o_id].remain)

    best_time = float("inf")
    best_plan = {}
    for device_id, state in states.items():  # 找到一个可分配任务的设备
        if state[0] == 0 or (state[1] != 'None' and
                state[0] == -1 and state[3] > DEVICE[device_id].crafts[state[1]].changeTime):  # 可安排生产,选取最优生产

            available_actions = DEVICE[device_id].available_actions(materials, state, k)
            if not available_actions:  # 无可生产项目，等待
                if state[0] == 0:  # 原本在待安排状态
                    state[0] = -1
                    state[3] = 0
                    best_time, best_plan = schedule(states, materials)
                    break
            # 若原本在等待状态，则继续查找下一个设备

            else:  # 遍历所有可选动作，选取最优
                for action in available_actions:
                    # print(action)
                    m_id = action[0]
                    o_id = action[1]
                    production_time = action[2]
                    child_states = dict(states)
                    child_materials = copy.deepcopy(materials)
                    if state[1] != 'None':  # 之前有生产
                        if DEVICE[device_id].crafts[state[1]].line_id == DEVICE[device_id].crafts[m_id].line_id:
                            child_states[device_id][0] = production_time
                        else:  # 换线
                            child_states[device_id][0] = production_time + DEVICE[device_id].crafts[state[1]].changeTime
                    child_states[device_id][1] = m_id
                    child_states[device_id][2] = o_id
                    child_best_time, child_best_plan = schedule(child_states, child_materials)
                    if child_best_time < best_time:
                        best_time = child_best_time
                        best_plan = child_best_plan
                break
    return best_time + next_time, best_plan

def set_demand(m_id, o_id, quantity):
    mat = MATERIAL[m_id][o_id]
    mat.demand += quantity
    for child, amount in mat.bom:
        if float(amount) > 0:
            if type(MATERIAL[child]) == dict:
                set_demand(child, o_id, quantity * amount)
            else:
                MATERIAL[child].demand += quantity * amount
    return

device_states = {}  # every value is a list: [设备生产此任务剩余时间(-1：等待中, 0:无任务，待安排), 工艺m_id, 订单o_id, 已等待时间]
for d_id in DEVICE.keys():
    device_states[d_id] = [0, "None", "None", 0]

orderML, order_craft = get_oder()

for o_id, order_mat in orderML.items():
    set_demand(order_mat.bom[0][0], o_id, order_mat.bom[0][1])

# for m_id in MATERIAL.keys():
#     if type(MATERIAL[m_id]) == dict:
#         for o_id in MATERIAL[m_id].keys():
#             print(MATERIAL[m_id][o_id].demand)

overall_best_time, overall_best_plan = schedule(device_states, MATERIAL)
print(overall_best_time)
