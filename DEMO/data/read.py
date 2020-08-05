# from MDP.modules_v3 import Material, Craft, Device, Stage, DECISION_INTERVAL
from MDP.modules_v5 import Material, Craft, Device, Stage, DECISION_INTERVAL


import pandas as pd
import numpy as np
import random as rd


std_out = False

device_pd = pd.read_csv('data/sample/device.csv', sep=',')  # 设备编号,班次
craft_pd = pd.read_csv('data/sample/craft.csv', sep=',')  # 设备编号,物料编码,产量,换线时间,工作中心编码,换线时间,连续生产类别编码,销售订单号
order_pd = pd.read_csv('data/sample/order.csv', sep=',')  # 订单编号        产品编号     产品量
bom_pd = pd.read_csv('data/sample/bom.csv', sep=',')  # 销售订单行号 母件编码 子件编码 定额 单位 采购 半成品 成品 子工序

MATERIAL = {}
DEVICE = {}
STAGE = {}
STAGE_name = []

STAGE_P_M = {}
M_T_STAGE = {}

Producing_Table = {}
#物料，设备两个下标确定该设备生产该物料的产量
Consuming_Table = {}
#物料，设备两个下标确定（该设备消耗该物料的量，母件，订单号）（单位时间内）
Max_Consume_Table = {}
#物料一个下标确定消耗物料速度最快的设备以及其在DECISION_INTERVAL内的消耗量

#初始化物料
M_INIT = {}
for index, row in bom_pd.iterrows():
    c_id = str(row['子件编码'])
    c = row['采购'] == '是'
    if c and (not c_id in M_INIT):
        M_INIT[c_id] = {}
        M_INIT[c_id]['type'] = False
        M_INIT[c_id]['bom'] = {}

    m_id = str(row['母件编码'])
    if not m_id in M_INIT.keys():
        M_INIT[m_id] = {}
        M_INIT[m_id]['type'] = True
        M_INIT[m_id]['bom'] = {}

    stage = row['子工序']
    if stage in STAGE_P_M.keys():
        if not m_id in STAGE_P_M[stage]:
            STAGE_P_M[stage].add(m_id)
    else:
        STAGE_P_M[stage] = {m_id}
    M_T_STAGE[m_id] = stage

    o_id = row['销售订单行号']
    if o_id in M_INIT[m_id]['bom']:
        M_INIT[m_id]['bom'][o_id].append([str(row['子件编码']), row['定额']])
    else:
        M_INIT[m_id]['bom'][o_id] = [[str(row['子件编码']), row['定额']], ]

for m_id in M_INIT.keys():
    if M_INIT[m_id]['type']:
        MATERIAL[m_id] = {}
        for o_id in M_INIT[m_id]['bom'].keys():
            MATERIAL[m_id][o_id] = Material(id=m_id, type=True, bom=M_INIT[m_id]['bom'][o_id], remain=0)
    else:
        MATERIAL[m_id] = Material(id=m_id, type=False, bom=None, remain=float('inf'))
del M_INIT

print('# all materials')
for s in MATERIAL.keys():
    if std_out:
        print(s, MATERIAL[s])

D_INIT = {}
STAGE_U_D = {}
D_T_STAGE = {}
D_P_M = {}
#初始化工艺
for index, row in craft_pd.iterrows():
    d_id = row['设备编号']
    m_id = str(row['物料编码'])
    p = row['产量']
    cT = row['换线时间']
    # stage = row['工作中心编码']
    stage = M_T_STAGE[m_id]

    craft = Craft(d_id=d_id, m_id=m_id, target=(MATERIAL[m_id], p), changeTime=cT)

    if stage in STAGE_U_D.keys():
        STAGE_U_D[stage].add(d_id)
    else:
        STAGE_U_D[stage] = {d_id}
    if d_id in D_T_STAGE:
        D_T_STAGE[d_id].add(stage)
    else:
        D_T_STAGE[d_id] = {stage}

    if d_id in D_P_M:
        D_P_M[d_id].add(m_id)
    else:
        D_P_M[d_id] = {m_id}


    if not d_id in D_INIT:
        D_INIT[d_id] = {}
    D_INIT[d_id][m_id] = craft

    if m_id not in Producing_Table:
        Producing_Table[m_id] = {}
    Producing_Table[m_id][d_id] = p

#将产量表排序
for m_id in Producing_Table:
    current_table = Producing_Table[m_id]
    current_table = sorted(current_table.items(), key=lambda x: x[1], reverse=True)
    Producing_Table[m_id] = current_table

#构建消耗表
for m_id in MATERIAL:
    if type(MATERIAL[m_id]) == dict:
        for o_id in MATERIAL[m_id]:
            bom = MATERIAL[m_id][o_id].bom
            for lower_level_material_info in bom:
                lower_level_material = lower_level_material_info[0]
                conosuming_rate = lower_level_material_info[1]
                if lower_level_material not in Consuming_Table:
                    Consuming_Table[lower_level_material] = {}
                for d_id, p in Producing_Table[m_id]:
                    if p == Producing_Table[m_id][0][1]:
                        Consuming_Table[lower_level_material][d_id] = (p * conosuming_rate, m_id, o_id)
                    else:
                        break

#构建最大消耗表，并将信信息加入MATERIAL
for material in Consuming_Table:
    current_table = Consuming_Table[material]
    Consuming_Table[material] = sorted(current_table.items(), key=lambda x: x[1][0], reverse=True)
    current_table = Consuming_Table[material]#这个是不是可以省略，我不是特别理解copy的问题，还是老老实实加上去了
    for i in range(len(current_table)):
        if current_table[i][1][0] == current_table[0][1][0]:
            consumed = Consuming_Table[material][0][1][0] * DECISION_INTERVAL
            if material not in Max_Consume_Table:
                Max_Consume_Table[material] = []
            Max_Consume_Table[material].append([Consuming_Table[material][i][0], (consumed, Consuming_Table[material][i][1][1], Consuming_Table[material][i][1][2])])
            
        else:
            break
    if type(MATERIAL[material]) == dict:
        for o_id in MATERIAL[material]:
            MATERIAL[material][o_id].bottom = (Max_Consume_Table[material][0][1][0], Max_Consume_Table[material][0][1][1])
    else:
        MATERIAL[material].bottom = (Max_Consume_Table[material][0][1][0], Max_Consume_Table[material][0][1][1])

#初始化设备
# operation = {
#     '早班': [1,0,0],
#     '中班': [0,1,0],
#     '晚班': [0,0,1]
# }
# for index, row in device_pd.iterrows():
#     d_id = row['设备编号']
#     DEVICE[d_id] = Device(id=d_id, crafts=D_INIT[d_id], operatingHours=operation[row['班次']])

print('# all device')
for d_id in D_INIT:
    if std_out:
        print(d_id, D_INIT[d_id])
    DEVICE[d_id] = Device(id=d_id, crafts=D_INIT[d_id])

#初始化阶段
for stage in STAGE_U_D.keys():
    stage_materials = {}
    for m_id in STAGE_P_M[stage]:
        stage_materials[m_id] = MATERIAL[m_id]
    STAGE[stage] = Stage(name=stage, materials=stage_materials,
                         devices=[DEVICE[d_id] for d_id in STAGE_U_D[stage]])

print('# all stage')
for s_id in STAGE.keys():
    if std_out:
        print(STAGE[s_id])

#初始化订单

def get_oder():

    orderML = {}
    for index, row in order_pd.iterrows():
        o_id = row['订单编号']
        m_id = str(row['产品编号'])
        quatity = row['产品量']
        orderML[o_id] = Material(id='order', type=True, bom=[[m_id, quatity],])

    order_craft = Craft(d_id='order', m_id='order', target=(orderML, 1), changeTime=0)
    return orderML, order_craft
#
# # 形成有向无环图
# edge = {}
# count = {s_id:0 for s_id in STAGE_P_M.keys()}
# for stage in STAGE_P_M.keys():
#     if not stage in edge.keys():
#         edge[stage] = []
#     for m in STAGE_P_M[stage]:
#         material = list(MATERIAL[m].values())[0]
#         for source, _ in material.bom:
#             if source in M_T_STAGE.keys():
#                 source_stage = M_T_STAGE[source]
#                 if not source_stage in edge[stage]:
#                     edge[stage].append(source_stage)
#                     count[source_stage] += 1
#
# print('# 工序产品依赖')
# for s_id in count.keys():
#     if std_out:
#         print(s_id, edge[s_id], count[s_id])
#
# print('# 工序顺序')
# while True:
#     flag = True
#     for s_id in count.keys():
#         if count[s_id] == 0:
#             break
#     if count[s_id] > 0:
#         if std_out:
#             print('error in construct graph!')
#         break
#     for next_s in edge[s_id]:
#         count[next_s] -= 1
#     STAGE_name.append(s_id)
#     del count[s_id]
#     if len(count) == 0:
#         if std_out:
#             print('stage seq:', STAGE_name)
#         break
#
# print('# 冲突设备')
# for index, s1_id in enumerate(STAGE_name[:-1]):
#     for s2_id in STAGE_name[index+1:]:
#         co_devices = set(STAGE[s1_id].devices) & set(STAGE[s2_id].devices)
#         if len(co_devices):
#             if std_out:
#                 print(s1_id,s2_id, '存在冲突设备',[d.id for d in co_devices])


# DEVICE_cloud = []
# print('# 找到具有相同工艺集的设备')
# for d_id in DEVICE.keys():
#     flag = True
#     for item in DEVICE_cloud:
#         if item['set'] == D_T_STAGE[d_id]:
#             item['devices'].append(d_id)
#             flag = False
#             break
#     if flag:
#         item = {
#             'set': D_T_STAGE[d_id],
#             'devices': [d_id,]
#         }
#         DEVICE_cloud.append(item)
#
# for item in DEVICE_cloud:
#     print(item['set'], item['devices'])
#
# DEVICE_cloud2 = []
# print('# 找到具有相同生产集的设备')
# for d_id in DEVICE.keys():
#     flag = True
#     for item in DEVICE_cloud2:
#         if item['set'] == D_P_M[d_id]:
#             item['devices'].append(d_id)
#             flag = False
#             break
#     if flag:
#         item = {
#             'set': D_P_M[d_id],
#             'devices': [d_id,]
#         }
#         DEVICE_cloud2.append(item)
#
# for item in DEVICE_cloud2:
#     print(item['set'], item['devices'])

HT = {
    'm_id': set(STAGE_P_M['外护子工序']) | set(STAGE_P_M['内护子工序']),
    'd_id': (set(STAGE_U_D['外护子工序']) | set(STAGE_U_D['内护子工序'])) - set(STAGE_U_D['加强件子工序']),
}
CL = {
    'm_id': set(STAGE_P_M['二次成缆子工序']) | set(STAGE_P_M['成缆子工序']),
    'd_id': set(STAGE_U_D['二次成缆子工序']) | set(STAGE_U_D['成缆子工序']),
}
JQJ = {
    'm_id': set(STAGE_P_M['加强件子工序']) | set(STAGE_P_M['外护子工序']) | set(STAGE_P_M['内护子工序']),
    'd_id': set(STAGE_U_D['加强件子工序']),
}
TS = {
    'm_id': set(STAGE_P_M['套塑子工序']),
    'd_id': set(STAGE_U_D['套塑子工序']),
}
ZS = {
    'm_id': set(STAGE_P_M['着色子工序']),
    'd_id': set(STAGE_U_D['着色子工序']),
}

Artificial_STAGE_INIT = {
    # 'HT': HT,
    'CL': CL,
    'JQJ': JQJ,
    'TS': TS,
    'ZS': ZS
}
# Artificial_STAGE_name = ['HT', 'CL', 'JQJ', 'TS', 'ZS']
Artificial_STAGE_name = ['CL', 'JQJ', 'TS', 'ZS']
Artificial_STAGE = {}
for stage in Artificial_STAGE_name:
    stage_materials = {m_id: MATERIAL[m_id] for m_id in Artificial_STAGE_INIT[stage]['m_id']}
    Artificial_STAGE[stage] = Stage(name=stage, materials=stage_materials,
                         devices=[DEVICE[d_id] for d_id in Artificial_STAGE_INIT[stage]['d_id']])


print('# all Artificial STAGE')
for s_id in Artificial_STAGE_name:
    if std_out:
        print(Artificial_STAGE[s_id])


def generate_virtual_order(level):
    orderml = {}
    level = max(0.05, level)
    for index, row in order_pd.iterrows():
        ratio = rd.random() * level
        o_id = row['订单编号']
        m_id = str(row['产品编号'])
        quatity = row['产品量'] * ratio
        orderml[o_id] = Material(id='order', type=True, bom=[[m_id, quatity], ])
    order_craft = Craft(d_id='order', m_id='order', target=(orderml, 1), changeTime=0)
    return orderml, order_craft


def curriculum_order(mask,ratio):
    orderml = {}
    for index, row in order_pd.iterrows():
        o_id = row['订单编号']
        m_id = str(row['产品编号'])
        quatity = row['产品量'] * ratio * mask[index]
        orderml[o_id] = Material(id='order', type=True, bom=[[m_id, quatity], ])
    order_craft = Craft(d_id='order', m_id='order', target=(orderml, 1), changeTime=0)
    return orderml, order_craft


for m_id in MATERIAL:
    #print(Max_Consume_Table[material])
    if type(MATERIAL[m_id]) == dict:
        for o_id in MATERIAL[m_id]:
            material = MATERIAL[m_id][o_id]
            if std_out:
                print(o_id, m_id, material.bottom)
    else:
        material = MATERIAL[m_id]
        if std_out:
            print(o_id, m_id, material.bottom)