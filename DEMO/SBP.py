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

