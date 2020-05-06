from MDP.modules import DECISION_INTERVAL
from data.read import MATERIAL, STAGE, order_craft, STAGE_name, Artificial_STAGE_name, Artificial_STAGE
from Controller.agents import init_Agents
from MemoryBuffer.Memory import MemoryBuffer
from MDP.reward import REWARD_RUlE

Peice = 60 * 8
Day = 3
TIMELIMIT = 7 * 24 * 60


# 初始化每轮的设备从devices中取得 stage_id: devices_list (str:[Device]
devicesInStages  = {}

memoryBuffer = MemoryBuffer()

#初始化agents
all_agents = {}
for stage_id in Artificial_STAGE_name:
    # stages[stage_id].set_devices(devicesInStages[stage_id])
    stage_info = Artificial_STAGE[stage_id].info()
    agents = init_Agents(stage_info=stage_info)
    all_agents[stage_id] = agents


def tToClock(t):
    p = t // Peice
    p = p % Day
    return p


# MDP
def episode():
    t = 0

    while True:
        p = tToClock(t)
        # 首先是订单stage,
        if order_craft.order_act(time_step=t, materials=MATERIAL):
            memoryBuffer.add_reward((TIMELIMIT - t ) * REWARD_RUlE['success'])
            break

        # 自上而下的决策stage
        # for stage_id in stage_names:
        #     STAGE[s_id].set_demand()
        #     stages[stage_id].stage_sequantial_step(agents=all_agents[stage_id], memoryBuffer=memoryBuffer, clock=p, t=t, log=True)

        for s_id in STAGE_name:
            STAGE[s_id].set_demand()
        for s_id in Artificial_STAGE_name:
            Artificial_STAGE[s_id].stage_sequantial_step(agents=all_agents[stage_id], memoryBuffer=memoryBuffer, clock=p, t=t, log=True)

        # Materials 数据更新
        [MATERIAL[id].clear() for id in MATERIAL.keys()]

        t += DECISION_INTERVAL
        if t > TIMELIMIT:
            memoryBuffer.add_reward(REWARD_RUlE['fail'] * order_craft.remain_order_demand())
            break



