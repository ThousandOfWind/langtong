from data.read2 import MATERIAL, DEVICE, get_oder, M_T_STAGE, NAMES
import copy
import sys
import matplotlib.pyplot as plt
import csv

sys.setrecursionlimit(10000)
DEMAND = {}  # 需求
REMAIN = {}  # 剩余
SCHEDULED = {}  # 已安排的生产
DEVICE_STATES = {}  # every value is a list: [设备生产此任务剩余时间(-1：等待中, 0:无任务，待安排, -2: 与 -1 相同，但跳过本次), 工艺m_id, 订单o_id, 已等待时间, 换线剩余时间]
SEARCH_STEP = 60  # 时间粒度
PRODUCTION_STEP = 60  # 生产划分粒度
BEST_SO_FAR = float('inf')
DEVICE_ID = list(DEVICE.keys())
COLORS = {}  # 颜色
COLOR_TYPES = [[255, 0, 0], [0, 0, 255], [0, 255, 0], [135, 135, 0], [0, 135, 135], [135, 0, 135]]
FILE_NUM = 0
headers = ['销售订单行号', '产品编码', '产品名称', '母件编码', '子件编码', '子件名称', '子工序', '子工序名称', '数量',
           '子件编码对应的属性', '任务号', '前置任务号', '后置任务号', '开始时间', '完成时间', '设备编号']


def gantt(plan):
    print(plan)
    plt.figure(figsize=(50, 50))
    for i in range(len(DEVICE_ID)):
        prod_list = plan[DEVICE_ID[i]]
        for j in range(len(prod_list)):
            production = prod_list[j]
            m_id = production[0]
            o_id = production[1]
            start_time = production[2]
            production_time = production[3]
            plt.barh(DEVICE_ID[i], production_time, left=start_time, color=rgb_to_hex(COLORS[m_id][o_id]))
            plt.text(start_time, DEVICE_ID[i], '%s\n%s'%(m_id, o_id))
    plt.yticks(DEVICE_ID)
    plt.show()
    return


def rgb_to_hex(color):
    strn = '#'
    for rgb in color:
        strn += str(hex(rgb))[-2:].replace('x', '0').upper()
    return strn


def color_reduce(color):
    ret = []
    for rgb in color:
        if rgb <= 215:
            ret.append(rgb + 40)
        else:
            ret.append(rgb)
    return ret


def set_demand(m_id, o_id, quantity):
    mat = MATERIAL[m_id][o_id]
    DEMAND[m_id][o_id] += quantity
    for source, amount in mat.bom:
        if float(amount) > 0:
            if type(MATERIAL[source]) == dict:
                if source not in COLORS.keys():
                    COLORS[source] = {}
                COLORS[source][o_id] = color_reduce(COLORS[m_id][o_id])
                set_demand(source, o_id, quantity * amount)
            else:
                DEMAND[source] += quantity * amount
    return

def available_actions(d_id, remain, scheduled):
    avail_actions = []
    device = DEVICE[d_id]
    for m_id, m_craft in device.crafts.items():
        craft = device.crafts[m_id]
        for o_id in craft.source.keys():
            if DEMAND[m_id][o_id] > scheduled[m_id][o_id] * 1.0001:
                flag = 1
                required_production_time = min(PRODUCTION_STEP, (DEMAND[m_id][o_id] - scheduled[m_id][o_id]) / craft.productivity)
                for s, com in craft.source[o_id]:
                    if type(MATERIAL[s]) == dict:
                        if com * craft.productivity * required_production_time > remain[s][o_id] * 1.0001:
                            flag = 0
                            break
                if flag == 1:
                    avail_actions.append(
                        [m_id, o_id, required_production_time, required_production_time * craft.productivity, scheduled[m_id][o_id]])
    return avail_actions


def produce(remain, m_id, o_id, d_id, time):
    craft = DEVICE[d_id].crafts[m_id]
    remain[m_id][o_id] += craft.productivity * time
    for s, com in craft.source[o_id]:
        if type(MATERIAL[s]) == dict:
            remain[s][o_id] -= com * craft.productivity * time
            # if remain[s][o_id] < 0:
            #     print("not enough material:", m_id, remain[s][o_id])


def result_to_csv(plans):
    global FILE_NUM
    FILE_NUM += 1
    rows = []
    for dev_id, plan in plans.items():
        device = DEVICE[dev_id]
        for production in plan:
            m_id = production[0]
            craft = device.crafts[m_id]
            o_id = production[1]
            start_time = production[2]
            duration = production[3]
            finish_time = duration + start_time
            for source, amount in craft.source[o_id]:
                if type(MATERIAL[source]) == dict:
                    s_type = '半成品'
                else:
                    s_type = '原材料'
                rows.append([o_id, orderML[o_id].bom[0][0], NAMES[orderML[o_id].bom[0][0]], m_id, NAMES[m_id], source, NAMES[source], M_T_STAGE[m_id], duration * amount, s_type, 0, 0, 0, start_time, finish_time, dev_id])
    with open('result' + str(FILE_NUM) + '.csv', 'w') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(rows)
    print("write complete")


def schedule(current_time, remain, scheduled, device_states,current_plan):
    global BEST_SO_FAR
    global count
    global trials
    global trial_time
    global PRODUCTION_STEP
    # for m_id in MATERIAL.keys():
    #     if type(MATERIAL[m_id]) == dict:
    #         for o_id in MATERIAL[m_id]:
    #             print(m_id, o_id, scheduled[m_id][o_id], remain[m_id][o_id], DEMAND[m_id][o_id])
    # print(dict(filter(lambda elem: elem[1][0] > 0, device_states.items())))
    # print("loop:", current_time)

    if current_time >= BEST_SO_FAR:
        count += 1
        return current_time + 10, {}
    completed = 1
    for o_id, order in orderML.items():  # 检查订单是否完成
        if order.bom[0][1] > remain[order.bom[0][0]][o_id] * 1.0001:
            completed = 0
    if completed == 1:
        # print("count", count)
        print("complete", current_time)
        print("count", count)
        gantt(current_plan)
        result_to_csv(current_plan)
        # trials += 1
        # trial_time.append(current_time)
        # if trials == 1000:
        #     plt.hist(trial_time)
        #     plt.show()
        #     exit(1)
        return current_time, {}

    for d_id, state in device_states.items():
        if state[0] == 0 or (state[1] != 'None' and
                             state[0] == -1 and state[3] > DEVICE[d_id].crafts[
                                 state[1]].changeTime) or (state[1] == "None" and state[0] == -1):  # 可安排生产,选取最优生产:
            actions = available_actions(d_id, remain, scheduled)
            actions.sort(key=lambda a: a[3])
            if not actions:  # 无可生产项目，等待
                if state[0] == 0:  # 原本在待安排状态
                    child_states = copy.deepcopy(device_states)
                    child_remain = copy.deepcopy(remain)
                    child_scheduled = copy.deepcopy(scheduled)
                    child_states[d_id][0] = -2
                    child_states[d_id][3] = 0
                    child_plan = copy.deepcopy(current_plan)
                    return schedule(current_time, child_remain, child_scheduled, child_states, child_plan)
                else:
                    continue
            best_time = float('inf')
            best_plan = {}
            for action in actions:
                m_id = action[0]
                o_id = action[1]
                production_time = action[2]
                production_amount = action[3]
                # print((m_id, o_id, production_amount, production_time, DEMAND[m_id][o_id], remain[m_id][o_id]))
                child_states = copy.deepcopy(device_states)
                child_remain = copy.deepcopy(remain)
                child_scheduled = copy.deepcopy(scheduled)
                child_plan = copy.deepcopy(current_plan)
                old_production_time = production_time
                if state[1] != "None":  # 之前有生产任务
                    if state[1] == m_id:  # 连续生产
                        child_states[d_id][0] = production_time
                        child_states[d_id][4] = 0
                        child_plan[d_id].append([m_id, o_id, current_time, production_time])
                        # if m_id == '8000066422':
                        #     print("no change", d_id, state[2], state[1], current_time, production_time)
                    else:  # 换线
                        if DEVICE[d_id].crafts[state[1]].changeTime >= production_time:
                            child_states[d_id][0] = production_time + DEVICE[d_id].crafts[state[1]].changeTime
                            child_states[d_id][4] = DEVICE[d_id].crafts[state[1]].changeTime
                            child_plan[d_id].append([m_id, o_id, current_time + DEVICE[d_id].crafts[state[1]].changeTime, production_time])
                        else:
                            child_states[d_id][0] = production_time
                            production_time -= DEVICE[d_id].crafts[state[1]].changeTime
                            child_states[d_id][4] = DEVICE[d_id].crafts[state[1]].changeTime
                            child_plan[d_id].append(
                                [m_id, o_id, current_time + DEVICE[d_id].crafts[state[1]].changeTime, production_time])
                else:
                    child_states[d_id][0] = production_time
                    child_states[d_id][4] = 0
                    child_plan[d_id].append([m_id, o_id, current_time, production_time])
                # if m_id == '8000001341' and o_id == '5000221032-40':
                #     print(child_scheduled[m_id][o_id], production_amount, current_time, d_id)
                # if current_time == 0 and d_id == 'ZS04':
                #     print(m_id, o_id, child_scheduled[m_id][o_id], production_amount, current_time, d_id)
                child_scheduled[m_id][o_id] += production_amount/old_production_time * production_time
                child_states[d_id][1] = m_id
                child_states[d_id][2] = o_id
                child_states[d_id][3] = 0
                child_best_time, child_best_plan = schedule(current_time, child_remain, child_scheduled, child_states, child_plan)
                if child_best_time < best_time:
                    best_time = child_best_time
                    best_plan = child_best_plan
                if best_time < BEST_SO_FAR:
                    BEST_SO_FAR = best_time
            return best_time, best_plan

    # 没有可安排生产的设备, 前进 SEARCH_STEP
    for d_id, state in device_states.items():
        if 0 < state[0] <= SEARCH_STEP:  # 本次时间跨度内能完成该生产
            produce(remain, state[1], state[2], d_id, state[0] - state[4])
            state[3] = SEARCH_STEP - state[0]
            state[0] = 0
            state[4] = 0
        elif state[0] > SEARCH_STEP:  # 按时间粒度生产
            if state[4] > 0:  # 先换线
                if state[4] > SEARCH_STEP:  # 本次时间跨度无法完成换线
                    state[0] -= SEARCH_STEP
                    state[4] -= SEARCH_STEP
                else:  # 先换线，然后生产
                    produce(remain, state[1], state[2], d_id, SEARCH_STEP - state[4])
                    state[0] -= SEARCH_STEP
                    state[4] = 0
            else:  # 直接生产
                produce(remain, state[1], state[2], d_id, SEARCH_STEP)
                state[0] -= SEARCH_STEP
        else:  # state[0] == -1 or -2
            state[3] += SEARCH_STEP
            state[0] = -1

    return schedule(current_time + SEARCH_STEP, remain, scheduled, device_states, current_plan)


orderML, order_craft = get_oder()

for m_id in MATERIAL.keys():
    if type(MATERIAL[m_id]) == dict:
        DEMAND[m_id] = {}
        REMAIN[m_id] = {}
        SCHEDULED[m_id] = {}
        for o_id in MATERIAL[m_id].keys():
            DEMAND[m_id][o_id] = 0
            REMAIN[m_id][o_id] = 0
            SCHEDULED[m_id][o_id] = 0
    else:
        DEMAND[m_id] = 0

c = 0
for o_id, order_mat in orderML.items():
    if order_mat.bom[0][0] not in COLORS.keys():
        COLORS[order_mat.bom[0][0]] = {}
    COLORS[order_mat.bom[0][0]][ o_id] = COLOR_TYPES[c]
    c += 1
    set_demand(order_mat.bom[0][0], o_id, order_mat.bom[0][1])

print(COLORS)

for d_id in DEVICE.keys():
    DEVICE_STATES[d_id] = [0, "None", "None", 0, 0]

count = 0
trials = 0
trial_time = []
init_plan = {}
for dev in DEVICE_ID:
    init_plan[dev] = []

overall_best_time, overall_best_plan = schedule(0, REMAIN, SCHEDULED, DEVICE_STATES, init_plan)
