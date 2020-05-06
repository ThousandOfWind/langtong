"""
需要定义实际涉及的物料，工艺，设备，状态
手工定义或通过config定义
"""
from .modules import Material, Craft, Device, Stage

# id:object (str:Material)
materials = {}

#
crafts = {}

#
devices = {}

#stage_names 是有序的stages.keys()
stage_names = []
stages = {}