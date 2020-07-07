from data.read2 import MATERIAL, DEVICE, get_oder
from data.create_map import Equipment_Relation_Map
import copy
import sys

sys.setrecursionlimit(50000)
k = 1  # 每份订单分成k份
device_states = {}  # every value is a list: [设备生产此任务剩余时间(-1：等待中, 0:无任务，待安排), 工艺m_id, 订单o_id, 已等待时间, 换线剩余时间]


def schedule(states, materials):
    print(states)
    next_time = float("inf")  # "快进"时间
    flag = 1
    for device, state in states.items():
        if 0 < state[0] < next_time:  # "快进"至最近结束的任务
            next_time = state[0]
        if 0 < state[4] < next_time:
            next_time = state[4]
        if state[0] == 0:
            flag = 0

    if next_time == float("inf") and flag == 1:
        # print(states)
        next_time = 5
        # for device, state in states.items():
        #     if state[0] == -1:
        #         state[3] += 5
        # return schedule(states, materials)

    if flag == 1:  # 没有待安排的设备，可快进至 next_time， 并完成对应生产
        for device_id, state in states.items():
            if state[0] > 0:
                if state[4] <= 0:
                    state[0] -= next_time
                    DEVICE[device_id].crafts[state[1]].produce(state[2], next_time, materials)
                else:
                    state[0] -= next_time
                    state[4] -= next_time
            elif state[0] == -1:
                state[3] += next_time
    else:
        next_time = 0

    completed = 1
    for o_id, order in orderML.items():
        if order.bom[0][1] > materials[order.bom[0][0]][o_id].remain * 1.0001:
            completed = 0
    if completed == 1:
        print("complete")
        return next_time, {}

    # for m_id in materials.keys():
    #     if type(materials[m_id]) == dict:
    #         for o_id in materials[m_id].keys():
    #             print(m_id, o_id, materials[m_id][o_id].remain, materials[m_id][o_id].demand)
    # print('loop')

    best_time = float("inf")
    best_plan = {}
    for device_id, state in states.items():  # 找到一个可分配任务的设备
        if state[0] == 0 or (state[1] != 'None' and
                             state[0] == -1 and state[3] > DEVICE[device_id].crafts[
                                 state[1]].changeTime) or (state[1] == "None" and state[0] == -1):  # 可安排生产,选取最优生产

            available_actions = DEVICE[device_id].available_actions(materials, k)
            if not available_actions:  # 无可生产项目，等待
                # if device_id == "ZS22":
                #     print(materials["8000001365"]["5000221032-10"].remain, materials["8000000002"].remain, materials["8000225745"].remain)
                #     for key, c in DEVICE[device_id].crafts.items():
                #         print(c.m_id)
                if state[0] == 0:  # 原本在待安排状态
                    child_states = dict(states)
                    child_materials = copy.deepcopy(materials)
                    child_states[device_id][0] = -1
                    child_states[device_id][3] = 0
                    child_best_time, child_best_plan = schedule(child_states, child_materials)
                    if child_best_time < best_time:
                        best_time = child_best_time
                        best_plan = child_best_plan
                    return best_time + next_time, best_plan
            # 若原本在等待状态，则继续查找下一个设备

            else:  # 遍历所有可选动作，选取最优
                # print("actions                             actions:", available_actions)
                for action in available_actions:
                    # print("action:", action)
                    m_id = action[0]
                    o_id = action[1]
                    # print("amount:", m_id, o_id, materials[m_id][o_id].remain, materials[m_id][o_id].demand)
                    production_time = action[2]
                    production_amount = action[3]
                    child_states = dict(states)
                    child_materials = copy.deepcopy(materials)
                    if state[1] != 'None':  # 之前有生产任务
                        if DEVICE[device_id].crafts[state[1]].line_id == DEVICE[device_id].crafts[m_id].line_id:  # 连续生产
                            child_states[device_id][0] = production_time
                            child_states[device_id][4] = 0
                        else:  # 换线
                            child_states[device_id][0] = production_time + DEVICE[device_id].crafts[state[1]].changeTime
                            child_states[device_id][4] = DEVICE[device_id].crafts[state[1]].changeTime
                        child_materials[m_id][o_id].produce_refer(production_amount)
                    child_states[device_id][1] = m_id
                    child_states[device_id][2] = o_id
                    child_best_time, child_best_plan = schedule(child_states, child_materials)
                    if child_best_time < best_time:
                        best_time = child_best_time
                        best_plan = child_best_plan
                return best_time + next_time, best_plan
    # for m_id in materials.keys():
    #     if type(materials[m_id]) == dict:
    #         for o_id in materials[m_id].keys():
    #             print(m_id, o_id, materials[m_id][o_id].remain, materials[m_id][o_id].demand)
    # print('loop')
    return schedule(states, materials)


def set_demand(m_id, o_id, quantity):
    mat = MATERIAL[m_id][o_id]
    mat.demand += quantity
    for source, amount in mat.bom:
        # if m_id == "8000001365" and o_id == "5000221032-10":
        #     print(source, amount)
        if float(amount) > 0:
            if type(MATERIAL[source]) == dict:
                set_demand(source, o_id, quantity * amount)
            else:
                MATERIAL[source].demand += quantity * amount
    return

# print(MATERIAL["8000000002"].remain)
# print(MATERIAL["8000225745"].remain)

for d_id in DEVICE.keys():
    device_states[d_id] = [0, "None", "None", 0, 0]

orderML, order_craft = get_oder()

for o_id, order_mat in orderML.items():
    set_demand(order_mat.bom[0][0], o_id, order_mat.bom[0][1])

# for m_id in MATERIAL.keys():
#     if type(MATERIAL[m_id]) == dict:
#         for o_id in MATERIAL[m_id].keys():
#             print(MATERIAL[m_id][o_id].demand)

overall_best_time, overall_best_plan = schedule(device_states, MATERIAL)
print(overall_best_time)
