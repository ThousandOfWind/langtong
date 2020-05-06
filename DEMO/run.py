from MDP.modules import Material
from MDP.module_objects import materials, devices, stages, stage_names
from RL.agents import init_Agents


# 将订单初始化为Material
orderlist = {}
# 定义处理订单device的动作，即将所有未分配的产品(remain)按订单中产品的分布分发给订单, 为实际产品发布demand
def orderdevice():
    return


# 初始化每轮的设备从devices中取得 stage_id: devices_list (str:[Device]
devicesInStages  = {}


#初始化agents
all_agents = {}
for stage_id in stage_names:
    stages[stage_id].set_devices(devicesInStages[stage_id])
    stage_info = stages[stage_id].info
    agents = init_Agents(stage_info)
    all_agents[stage_id] = all_agents

# MDP
while True:
    # 首先是订单stage,
    orderdevice()

    # 自上而下的决策stage
    for stage_id in stage_names:
        stages[stage_id].step(all_agents[stage_id])

    # Materials 数据更新
    [materials[id].step() for id in materials.keys()]
