'''
对任意一个设备，寻找：
A上级材料设备
B下级产品设备
C重复职能设备
'''
import pandas as pd

#
# craft_pd = pd.read_csv('data/sample/craft.csv', sep=',')  #  设备编号,物料编码,产量,换线时间,工作中心编码,换线时间,连续生产类别编码,销售订单号
# bom_pd = pd.read_csv('data/sample/bom.csv', sep=',')  # 销售订单行号 母件编码 子件编码 定额 单位 采购 半成品 成品 子工序
craft_pd = pd.read_csv('c:/Users/xuean/Documents/GitHub/langtong/DEMO/data/sample/craft.csv', sep=',')  #  设备编号,物料编码,产量,换线时间,工作中心编码,换线时间,连续生产类别编码,销售订单号
bom_pd = pd.read_csv('c:/Users/xuean/Documents/GitHub/langtong/DEMO/data/sample/bom.csv', sep=',')  # 销售订单行号 母件编码 子件编码 定额 单位 采购 半成品 成品 子工序

Article_to_Equipment = {}
#物品->设备映射

Equipment_Relation_Map = {}
#设备关系表

for index, row in craft_pd.iterrows():
    '''
    初始化：建物品设备表，设备关系表赋初值
    '''
    Equipment_Code = str(row['设备编号'])
    Article_Code = str(row['物料编码'])
    Equipment_Relation_Map[Equipment_Code] = {'Lower_Level_Equipment': set({}), 'Higher_Level_Equipment': set({}), 'Counterparts': set({})}
    if Article_Code not in Article_to_Equipment:
        Article_to_Equipment[Article_Code] = set({})
    Article_to_Equipment[Article_Code].add(Equipment_Code)

print(Article_to_Equipment)
print('\n\n')

#处理相同功能设备问题
for article in Article_to_Equipment:
    for equipment in Article_to_Equipment[article]:
        Equipment_Relation_Map[equipment]['Counterparts'] = Equipment_Relation_Map[equipment]['Counterparts'] | Article_to_Equipment[article]
        
No_Equipment_Articles = set({})

for index, row in bom_pd.iterrows():
    child_id = str(row['子件编码'])
    parent_id = str(row['母件编码'])
    
    if child_id not in Article_to_Equipment:
        No_Equipment_Articles.add(child_id)
    elif parent_id not in Article_to_Equipment:
        No_Equipment_Articles.add(parent_id)

    #处理子母件问题（用set并）
    else:
        for lower_level_equipment in Article_to_Equipment[child_id]:
            Equipment_Relation_Map[lower_level_equipment]['Higher_Level_Equipment'] = (Equipment_Relation_Map[lower_level_equipment]['Higher_Level_Equipment'] | Article_to_Equipment[parent_id])
        for higher_level_equipment in Article_to_Equipment[parent_id]:
            Equipment_Relation_Map[higher_level_equipment]['Lower_Level_Equipment'] = Equipment_Relation_Map[higher_level_equipment]['Lower_Level_Equipment'] | Article_to_Equipment[child_id]

#排序输出
for equipment in Equipment_Relation_Map:
    Equipment_Relation_Map[equipment]['Higher_Level_Equipment'].discard(equipment)
    Equipment_Relation_Map[equipment]['Higher_Level_Equipment'] = sorted(Equipment_Relation_Map[equipment]['Higher_Level_Equipment'])
    Equipment_Relation_Map[equipment]['Lower_Level_Equipment'].discard(equipment)
    Equipment_Relation_Map[equipment]['Lower_Level_Equipment'] = sorted(Equipment_Relation_Map[equipment]['Lower_Level_Equipment'])
    Equipment_Relation_Map[equipment]['Counterparts'].discard(equipment)
    Equipment_Relation_Map[equipment]['Counterparts'] = sorted(Equipment_Relation_Map[equipment]['Counterparts'])
    print('Equipment_Code:%s' % equipment)
    print(Equipment_Relation_Map[equipment])
    print()

