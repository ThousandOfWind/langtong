from modules_v3 import DECISION_INTERVAL
from read import MATERIAL
import pandas as pd

craft_pd = pd.read_csv('c:/Users/xuean/Documents/GitHub/langtong/DEMO/data/sample/craft.csv', sep=',')  # 设备编号,物料编码,产量,换线时间,工作中心编码,换线时间,连续生产类别编码,销售订单号
bom_pd = pd.read_csv('c:/Users/xuean/Documents/GitHub/langtong/DEMO/data/sample/bom.csv', sep=',')  # 销售订单行号 母件编码 子件编码 定额 单位 采购 半成品 成品 子工序

Producing_Table = {}
#物料，设备两个下标确定该设备生产该物料的产量
Consuming_Table = {}
#物料，设备两个下标确定（该设备消耗该物料的量，母件，订单号）（单位时间内）
Max_Consume_Table = {}
#物料一个下标确定消耗物料速度最快的设备以及其在DECISION_INTERVAL内的消耗量


print('求材料单位时间内的最大消耗量')

for index, row in craft_pd.iterrows(): 
    d_id = row['设备编号']
    m_id = str(row['物料编码'])
    p = row['产量']
    cT = row['换线时间']
    cLine = row['连续生产类别编码']
    if m_id not in Producing_Table:
        Producing_Table[m_id] = {}
    Producing_Table[m_id][d_id] = p

for m_id in Producing_Table:
    current_table = Producing_Table[m_id]
    current_table = sorted(current_table.items(), key=lambda x: x[1], reverse=True)
    Producing_Table[m_id] = current_table
    
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


        
if __name__ == "__main__":
    print('排序后的生产表')
    for m_id in Producing_Table:
        print(m_id, ":")
        print(Producing_Table[m_id])
    print()

    print('排序后的材料消耗表')
    for material in Consuming_Table:
        print(material,':')
        print(Consuming_Table[material])
    print()
    
    for material in Max_Consume_Table:
        #print(Max_Consume_Table[material])
        for info in Max_Consume_Table[material]:
            print('物料{m_id}的最大消耗量（{t}min内）可以在设备{d_id}上完成，母件和订单号分别为：{p_id},{o_id},最大消耗量为{p}'.format(m_id=material, t=DECISION_INTERVAL, d_id=info[0], p_id=info[1][1], o_id=info[1][2], p=info[1][0]))