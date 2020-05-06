"""
需要定义实际涉及的物料，工艺，设备，状态
手工定义或通过config定义
"""
# from .modules import Material, Craft, Device, Stage
from MDP.modules import Material,Craft,Device,Stage

# 所有实际涉及到的物料（包括产品，半成品，原材料）被罗列在  materials 中
# "物料ID"：Material("物料ID"， 物料数量)
# 作为原材料是默认物料数量为无穷
materials = {"8000000002":Material("8000000002"),"8000001269":Material("8000001269",0),"8000001281":Material("8000001281",0),
             "8000001293":Material("8000001293",0),"8000001305":Material("8000001305",0),"8000001317":Material("8000001317",0),
             "8000001329":Material("8000001329",0),"8000001341":Material("8000001341",0),"8000001353":Material("8000001353",0),
             "8000001365":Material("8000001365",0),"8000001377":Material("8000001377",0),"8000001389":Material("8000001389",0),
             "8000001401":Material("8000001401",0),"8000001413":Material("8000001413",0),"8000030244":Material("8000030244",0),
             "8000030245":Material("8000030245",0),"8000030246":Material("8000030246",0),"8000030247":Material("8000030247",0),
             "8000030248":Material("8000030248",0),"8000030249":Material("8000030249",0),"8000030250":Material("8000030250",0),
             "8000030251":Material("8000030251",0),"8000030252":Material("8000030252",0),"8000030253":Material("8000030253",0),
             "8000030254":Material("8000030254",0),"8000030255":Material("8000030255",0),"8000031456":Material("8000031456",0),
             "8000031594":Material("8000031594",0),"8000031595":Material("8000031595",0),"8000031596":Material("8000031596",0),
             "8000031597":Material("8000031597",0),"8000031606":Material("8000031606",0),"8000032881":Material("8000032881",0),
             "8000051658":Material("8000051658"),"8000051867":Material("8000051867",0),"8000055182":Material("8000055182",0),
             "8000066422":Material("8000066422",0),"8000066442":Material("8000066442",0),"8000147753":Material("8000147753",0),
             "8000203645":Material("8000203645",0),"8000222321":Material("8000222321"),"8000223845":Material("8000223845"),
             "8000223847":Material("8000223847"),"8000223849":Material("8000223849"),"8000223851":Material("8000223851"),
             "8000224416":Material("8000224416"),"8000224419":Material("8000224419"),"8000224420":Material("8000224420"),
             "8000224485":Material("8000224485"),"8000224609":Material("8000224609"),"8000224613":Material("8000224613"),
             "8000224614":Material("8000224614"),"8000224615":Material("8000224615"),"8000224616":Material("8000224616"),
             "8000224617":Material("8000224617"),"8000224619":Material("8000224619"),"8000224620":Material("8000224620"),
             "8000224621":Material("8000224621"),"8000225737":Material("8000225737"),"8000225738":Material("8000225738"),
             "8000225739":Material("8000225739"),"8000225740":Material("8000225740"),"8000225741":Material("8000225741"),
             "8000225742":Material("8000225742"),"8000225743":Material("8000225743"),"8000225744":Material("8000225744"),
             "8000225745":Material("8000225745"),"8000225746":Material("8000225746"),"8000225747":Material("8000225747"),
             "8000225748":Material("8000225748"),"8000225972":Material("8000225972"),"8000225974":Material("8000225974"),
             "8000232608":Material("8000232608"),"8000237152":Material("8000237152"),"8000239089":Material("8000239089"),
             "8000258325":Material("8000258325"),"8000269602":Material("8000269602",0),"8000270355":Material("8000270355",0),
             "8000270558":Material("8000270558",0),"8000270999":Material("8000270999",0),"8000272510":Material("8000272510"),
             "8000275010":Material("8000275010"),"8000275219":Material("8000275219"),"8000281692":Material("8000281692"),
             "8000282876":Material("8000282876",0),"8000283379":Material("8000283379"),"8000283700":Material("8000283700"),
             "8000284363":Material("8000284363",0),"8000284390":Material("8000284390",0),"8000286138":Material("8000286138",0)}

# 每台设备的生产某样产品的产能被罗列在crafts中
# "设备ID_产品ID"：Craft(id="设备ID_产品ID", target=(materials["产品ID"], 每分钟产量）， source=[(materials["子件ID"], 每分钟消耗量), operatingHours=[1,1,1]]
# operatingHours 的三个维度对应早、晚、夜班， 默认三班均可工作
crafts = {'HT01_8000286138':Craft(id='HT01_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT02_8000286138':Craft(id='HT02_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT03_8000286138':Craft(id='HT03_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT04_8000286138':Craft(id='HT04_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT05_8000286138':Craft(id='HT05_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT06_8000286138':Craft(id='HT06_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT07_8000286138':Craft(id='HT07_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT08_8000286138':Craft(id='HT08_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT09_8000286138':Craft(id='HT09_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT10_8000286138':Craft(id='HT10_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT11_8000286138':Craft(id='HT11_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT12_8000286138':Craft(id='HT12_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT13_8000286138':Craft(id='HT13_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT15_8000286138':Craft(id='HT15_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT16_8000286138':Craft(id='HT16_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT17_8000286138':Craft(id='HT17_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT18_8000286138':Craft(id='HT18_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT19_8000286138':Craft(id='HT19_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT20_8000286138':Craft(id='HT20_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'HT21_8000286138':Craft(id='HT21_8000286138',target=(materials['8000286138'],0.06),source=[(materials['8000224416'],1.98864),(materials['8000239089'],0.0105),(materials['8000283379'],0.01926),(materials['8000272510'],0.01248),(materials['8000066422'],0.060479999999999985)],changeTime=40),
          'SZ01_8000066422':Craft(id='SZ01_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ02_8000066422':Craft(id='SZ02_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ03_8000066422':Craft(id='SZ03_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ04_8000066422':Craft(id='SZ04_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ05_8000066422':Craft(id='SZ05_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ06_8000066422':Craft(id='SZ06_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ07_8000066422':Craft(id='SZ07_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ08_8000066422':Craft(id='SZ08_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ09_8000066422':Craft(id='SZ09_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ10_8000066422':Craft(id='SZ10_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ11_8000066422':Craft(id='SZ11_8000066422',target=(materials['8000066422'],0.05),source=[(materials['8000031456'],0.0504),(materials['8000239089'],0.0109),(materials['8000275219'],0.0109),(materials['8000223845'],0.10500000000000001),(materials['8000283379'],0.01)],changeTime=30),
          'SZ12_8000066422':Craft(id='SZ12_8000066422',target=(materials['8000066422'],0.05),source=[(materials['8000031456'],0.0504),(materials['8000239089'],0.0109),(materials['8000275219'],0.0109),(materials['8000223845'],0.10500000000000001),(materials['8000283379'],0.01)],changeTime=30),
          'SZ13_8000066422':Craft(id='SZ13_8000066422',target=(materials['8000066422'],0.05),source=[(materials['8000031456'],0.0504),(materials['8000239089'],0.0109),(materials['8000275219'],0.0109),(materials['8000223845'],0.10500000000000001),(materials['8000283379'],0.01)],changeTime=30),
          'SZ15_8000066422':Craft(id='SZ15_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ16_8000066422':Craft(id='SZ16_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ17_8000066422':Craft(id='SZ17_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'SZ18_8000066422':Craft(id='SZ18_8000066422',target=(materials['8000066422'],0.08),source=[(materials['8000031456'],0.08064),(materials['8000239089'],0.017439999999999997),(materials['8000275219'],0.017439999999999997),(materials['8000223845'],0.16799999999999998),(materials['8000283379'],0.016)],changeTime=30),
          'TS05_8000031456':Craft(id='TS05_8000031456',target=(materials['8000031456'],0.18),source=[(materials['8000224609'],0.5284800022439532),(materials['8000225972'],0.24156000507842032),(materials['8000001293'],0.18144000525557444),(materials['8000001365'],0.18144000525557444)],changeTime=30),
          'TS16_8000031456':Craft(id='TS16_8000031456',target=(materials['8000031456'],0.12),source=[(materials['8000224609'],0.35232000149596876),(materials['8000225972'],0.16104000338561353),(materials['8000001293'],0.1209600035037163),(materials['8000001365'],0.1209600035037163)],changeTime=30),
          'ZS01_8000001293':Craft(id='ZS01_8000001293',target=(materials['8000001293'],1.7),source=[(materials['8000000002'],1.7136000022131253),(materials['8000225739'],0.010200018949887394)],changeTime=5),
          'ZS01_8000001365':Craft(id='ZS01_8000001365',target=(materials['8000001365'],1.7),source=[(materials['8000225745'],0.010200018949887394),(materials['8000000002'],1.7136000022131253)],changeTime=5),
          'ZS02_8000001293':Craft(id='ZS02_8000001293',target=(materials['8000001293'],1.7),source=[(materials['8000000002'],1.7136000022131253),(materials['8000225739'],0.010200018949887394)],changeTime=5),
          'ZS02_8000001365':Craft(id='ZS02_8000001365',target=(materials['8000001365'],1.7),source=[(materials['8000225745'],0.010200018949887394),(materials['8000000002'],1.7136000022131253)],changeTime=5),
          'ZS03_8000001293':Craft(id='ZS03_8000001293',target=(materials['8000001293'],1.7),source=[(materials['8000000002'],1.7136000022131253),(materials['8000225739'],0.010200018949887394)],changeTime=5),
          'ZS03_8000001365':Craft(id='ZS03_8000001365',target=(materials['8000001365'],1.7),source=[(materials['8000225745'],0.010200018949887394),(materials['8000000002'],1.7136000022131253)],changeTime=5),
          'ZS04_8000001293':Craft(id='ZS04_8000001293',target=(materials['8000001293'],1.7),source=[(materials['8000000002'],1.7136000022131253),(materials['8000225739'],0.010200018949887394)],changeTime=5),
          'ZS04_8000001365':Craft(id='ZS04_8000001365',target=(materials['8000001365'],1.7),source=[(materials['8000225745'],0.010200018949887394),(materials['8000000002'],1.7136000022131253)],changeTime=5),
          'ZS05_8000001293':Craft(id='ZS05_8000001293',target=(materials['8000001293'],1.2),source=[(materials['8000000002'],1.2096000015622062),(materials['8000225739'],0.0072000133763911005)],changeTime=5),
          'ZS05_8000001365':Craft(id='ZS05_8000001365',target=(materials['8000001365'],1.2),source=[(materials['8000225745'],0.0072000133763911005),(materials['8000000002'],1.2096000015622062)],changeTime=5),
          'ZS06_8000001293':Craft(id='ZS06_8000001293',target=(materials['8000001293'],1.2),source=[(materials['8000000002'],1.2096000015622062),(materials['8000225739'],0.0072000133763911005)],changeTime=5),
          'ZS06_8000001365':Craft(id='ZS06_8000001365',target=(materials['8000001365'],1.2),source=[(materials['8000225745'],0.0072000133763911005),(materials['8000000002'],1.2096000015622062)],changeTime=5),
          'ZS07_8000001293':Craft(id='ZS07_8000001293',target=(materials['8000001293'],2.0),source=[(materials['8000000002'],2.0160000026036773),(materials['8000225739'],0.012000022293985169)],changeTime=5),
          'ZS07_8000001365':Craft(id='ZS07_8000001365',target=(materials['8000001365'],2.0),source=[(materials['8000225745'],0.012000022293985169),(materials['8000000002'],2.0160000026036773)],changeTime=5),
          'ZS08_8000001293':Craft(id='ZS08_8000001293',target=(materials['8000001293'],1.2),source=[(materials['8000000002'],1.2096000015622062),(materials['8000225739'],0.0072000133763911005)],changeTime=5),
          'ZS08_8000001365':Craft(id='ZS08_8000001365',target=(materials['8000001365'],1.2),source=[(materials['8000225745'],0.0072000133763911005),(materials['8000000002'],1.2096000015622062)],changeTime=5),
          'ZS09_8000001293':Craft(id='ZS09_8000001293',target=(materials['8000001293'],1.2),source=[(materials['8000000002'],1.2096000015622062),(materials['8000225739'],0.0072000133763911005)],changeTime=5),
          'ZS09_8000001365':Craft(id='ZS09_8000001365',target=(materials['8000001365'],1.2),source=[(materials['8000225745'],0.0072000133763911005),(materials['8000000002'],1.2096000015622062)],changeTime=5),
          'ZS10_8000001293':Craft(id='ZS10_8000001293',target=(materials['8000001293'],1.2),source=[(materials['8000000002'],1.2096000015622062),(materials['8000225739'],0.0072000133763911005)],changeTime=5),
          'ZS10_8000001365':Craft(id='ZS10_8000001365',target=(materials['8000001365'],1.2),source=[(materials['8000225745'],0.0072000133763911005),(materials['8000000002'],1.2096000015622062)],changeTime=5),
          'ZS11_8000001293':Craft(id='ZS11_8000001293',target=(materials['8000001293'],1.2),source=[(materials['8000000002'],1.2096000015622062),(materials['8000225739'],0.0072000133763911005)],changeTime=5),
          'ZS11_8000001365':Craft(id='ZS11_8000001365',target=(materials['8000001365'],1.2),source=[(materials['8000225745'],0.0072000133763911005),(materials['8000000002'],1.2096000015622062)],changeTime=5),
          'ZS12_8000001293':Craft(id='ZS12_8000001293',target=(materials['8000001293'],1.2),source=[(materials['8000000002'],1.2096000015622062),(materials['8000225739'],0.0072000133763911005)],changeTime=5),
          'ZS12_8000001365':Craft(id='ZS12_8000001365',target=(materials['8000001365'],1.2),source=[(materials['8000225745'],0.0072000133763911005),(materials['8000000002'],1.2096000015622062)],changeTime=5),
          'ZS13_8000001293':Craft(id='ZS13_8000001293',target=(materials['8000001293'],1.2),source=[(materials['8000000002'],1.2096000015622062),(materials['8000225739'],0.0072000133763911005)],changeTime=5),
          'ZS13_8000001365':Craft(id='ZS13_8000001365',target=(materials['8000001365'],1.2),source=[(materials['8000225745'],0.0072000133763911005),(materials['8000000002'],1.2096000015622062)],changeTime=5),
          'ZS15_8000001293':Craft(id='ZS15_8000001293',target=(materials['8000001293'],1.2),source=[(materials['8000000002'],1.2096000015622062),(materials['8000225739'],0.0072000133763911005)],changeTime=5),
          'ZS15_8000001365':Craft(id='ZS15_8000001365',target=(materials['8000001365'],1.2),source=[(materials['8000225745'],0.0072000133763911005),(materials['8000000002'],1.2096000015622062)],changeTime=5),
          'ZS16_8000001293':Craft(id='ZS16_8000001293',target=(materials['8000001293'],1.0),source=[(materials['8000000002'],1.0080000013018386),(materials['8000225739'],0.006000011146992584)],changeTime=5),
          'ZS16_8000001365':Craft(id='ZS16_8000001365',target=(materials['8000001365'],1.0),source=[(materials['8000225745'],0.006000011146992584),(materials['8000000002'],1.0080000013018386)],changeTime=5),
          'ZS17_8000001293':Craft(id='ZS17_8000001293',target=(materials['8000001293'],1.0),source=[(materials['8000000002'],1.0080000013018386),(materials['8000225739'],0.006000011146992584)],changeTime=5),
          'ZS17_8000001365':Craft(id='ZS17_8000001365',target=(materials['8000001365'],1.0),source=[(materials['8000225745'],0.006000011146992584),(materials['8000000002'],1.0080000013018386)],changeTime=5),
          'ZS18_8000001293':Craft(id='ZS18_8000001293',target=(materials['8000001293'],1.0),source=[(materials['8000000002'],1.0080000013018386),(materials['8000225739'],0.006000011146992584)],changeTime=5),
          'ZS18_8000001365':Craft(id='ZS18_8000001365',target=(materials['8000001365'],1.0),source=[(materials['8000225745'],0.006000011146992584),(materials['8000000002'],1.0080000013018386)],changeTime=5),
          'ZS19_8000001293':Craft(id='ZS19_8000001293',target=(materials['8000001293'],1.0),source=[(materials['8000000002'],1.0080000013018386),(materials['8000225739'],0.006000011146992584)],changeTime=5),
          'ZS19_8000001365':Craft(id='ZS19_8000001365',target=(materials['8000001365'],1.0),source=[(materials['8000225745'],0.006000011146992584),(materials['8000000002'],1.0080000013018386)],changeTime=5),
          'ZS20_8000001293':Craft(id='ZS20_8000001293',target=(materials['8000001293'],1.0),source=[(materials['8000000002'],1.0080000013018386),(materials['8000225739'],0.006000011146992584)],changeTime=5),
          'ZS20_8000001365':Craft(id='ZS20_8000001365',target=(materials['8000001365'],1.0),source=[(materials['8000225745'],0.006000011146992584),(materials['8000000002'],1.0080000013018386)],changeTime=5),
          'ZS21_8000001293':Craft(id='ZS21_8000001293',target=(materials['8000001293'],1.0),source=[(materials['8000000002'],1.0080000013018386),(materials['8000225739'],0.006000011146992584)],changeTime=5),
          'ZS21_8000001365':Craft(id='ZS21_8000001365',target=(materials['8000001365'],1.0),source=[(materials['8000225745'],0.006000011146992584),(materials['8000000002'],1.0080000013018386)],changeTime=5),
          'ZS22_8000001293':Craft(id='ZS22_8000001293',target=(materials['8000001293'],1.0),source=[(materials['8000000002'],1.0080000013018386),(materials['8000225739'],0.006000011146992584)],changeTime=5),
          'ZS22_8000001365':Craft(id='ZS22_8000001365',target=(materials['8000001365'],1.0),source=[(materials['8000225745'],0.006000011146992584),(materials['8000000002'],1.0080000013018386)],changeTime=5),
          'ZS23_8000001293':Craft(id='ZS23_8000001293',target=(materials['8000001293'],1.0),source=[(materials['8000000002'],1.0080000013018386),(materials['8000225739'],0.006000011146992584)],changeTime=5),
          'ZS23_8000001365':Craft(id='ZS23_8000001365',target=(materials['8000001365'],1.0),source=[(materials['8000225745'],0.006000011146992584),(materials['8000000002'],1.0080000013018386)],changeTime=5),
          'ZS24_8000001293':Craft(id='ZS24_8000001293',target=(materials['8000001293'],1.0),source=[(materials['8000000002'],1.0080000013018386),(materials['8000225739'],0.006000011146992584)],changeTime=5),
          'ZS24_8000001365':Craft(id='ZS24_8000001365',target=(materials['8000001365'],1.0),source=[(materials['8000225745'],0.006000011146992584),(materials['8000000002'],1.0080000013018386)],changeTime=5),
          'ZS25_8000001293':Craft(id='ZS25_8000001293',target=(materials['8000001293'],1.2),source=[(materials['8000000002'],1.2096000015622062),(materials['8000225739'],0.0072000133763911005)],changeTime=5),
          'ZS25_8000001365':Craft(id='ZS25_8000001365',target=(materials['8000001365'],1.2),source=[(materials['8000225745'],0.0072000133763911005),(materials['8000000002'],1.2096000015622062)],changeTime=5),
          'ZS26_8000001293':Craft(id='ZS26_8000001293',target=(materials['8000001293'],1.5),source=[(materials['8000000002'],1.512000001952758),(materials['8000225739'],0.009000016720488876)],changeTime=5),
          'ZS26_8000001365':Craft(id='ZS26_8000001365',target=(materials['8000001365'],1.5),source=[(materials['8000225745'],0.009000016720488876),(materials['8000000002'],1.512000001952758)],changeTime=5)}

# 所有实际用到的设备被罗列在 devices中
# "设备ID": Device(id="设备ID",crafts=[crafts[设备可执行Craft ID]，]
devices = {'HT01':Device(id='HT01',crafts=[crafts['HT01_8000286138']]),'HT02':Device(id='HT02',crafts=[crafts['HT02_8000286138']]),'HT03':Device(id='HT03',crafts=[crafts['HT03_8000286138']]),
           'HT04':Device(id='HT04',crafts=[crafts['HT04_8000286138']]),'HT05':Device(id='HT05',crafts=[crafts['HT05_8000286138']]),'HT06':Device(id='HT06',crafts=[crafts['HT06_8000286138']]),
           'HT07':Device(id='HT07',crafts=[crafts['HT07_8000286138']]),'HT08':Device(id='HT08',crafts=[crafts['HT08_8000286138']]),'HT09':Device(id='HT09',crafts=[crafts['HT09_8000286138']]),
           'HT10':Device(id='HT10',crafts=[crafts['HT10_8000286138']]),'HT11':Device(id='HT11',crafts=[crafts['HT11_8000286138']]),'HT12':Device(id='HT12',crafts=[crafts['HT12_8000286138']]),
           'HT13':Device(id='HT13',crafts=[crafts['HT13_8000286138']]),'HT15':Device(id='HT15',crafts=[crafts['HT15_8000286138']]),'HT16':Device(id='HT16',crafts=[crafts['HT16_8000286138']]),
           'HT17':Device(id='HT17',crafts=[crafts['HT17_8000286138']]),'HT18':Device(id='HT18',crafts=[crafts['HT18_8000286138']]),'HT19':Device(id='HT19',crafts=[crafts['HT19_8000286138']]),
           'HT20':Device(id='HT20',crafts=[crafts['HT20_8000286138']]),'HT21':Device(id='HT21',crafts=[crafts['HT21_8000286138']]),
           'SZ01':Device(id='SZ01',crafts=[crafts['SZ01_8000066422']]),'SZ02':Device(id='SZ02',crafts=[crafts['SZ02_8000066422']]),
           'SZ03':Device(id='SZ03',crafts=[crafts['SZ03_8000066422']]),'SZ04':Device(id='SZ04',crafts=[crafts['SZ04_8000066422']]),'SZ05':Device(id='SZ05',crafts=[crafts['SZ05_8000066422']]),
           'SZ06':Device(id='SZ06',crafts=[crafts['SZ06_8000066422']]),'SZ07':Device(id='SZ07',crafts=[crafts['SZ07_8000066422']]),'SZ08':Device(id='SZ08',crafts=[crafts['SZ08_8000066422']]),
           'SZ09':Device(id='SZ09',crafts=[crafts['SZ09_8000066422']]),'SZ10':Device(id='SZ10',crafts=[crafts['SZ10_8000066422']]),'SZ11':Device(id='SZ11',crafts=[crafts['SZ11_8000066422']]),
           'SZ12':Device(id='SZ12',crafts=[crafts['SZ12_8000066422']]),'SZ13':Device(id='SZ13',crafts=[crafts['SZ13_8000066422']]),'SZ15':Device(id='SZ15',crafts=[crafts['SZ15_8000066422']]),
           'SZ16':Device(id='SZ16',crafts=[crafts['SZ16_8000066422']]),'SZ17':Device(id='SZ17',crafts=[crafts['SZ17_8000066422']]),'SZ18':Device(id='SZ18',crafts=[crafts['SZ18_8000066422']]),
           'TS05':Device(id='TS05',crafts=[crafts['TS05_8000031456']]),'TS16':Device(id='TS16',crafts=[crafts['TS16_8000031456']]),
           'ZS01':Device(id='ZS01',crafts=[crafts['ZS01_8000001365'],crafts['ZS01_8000001293']]),'ZS02':Device(id='ZS02',crafts=[crafts['ZS02_8000001365'],crafts['ZS02_8000001293']]),
           'ZS03':Device(id='ZS03',crafts=[crafts['ZS03_8000001293'],crafts['ZS03_8000001365']]),'ZS04':Device(id='ZS04',crafts=[crafts['ZS04_8000001293'],crafts['ZS04_8000001365']]),
           'ZS05':Device(id='ZS05',crafts=[crafts['ZS05_8000001293'],crafts['ZS05_8000001365']]),'ZS06':Device(id='ZS06',crafts=[crafts['ZS06_8000001365'],crafts['ZS06_8000001293']]),
           'ZS07':Device(id='ZS07',crafts=[crafts['ZS07_8000001365'],crafts['ZS07_8000001293']]),'ZS08':Device(id='ZS08',crafts=[crafts['ZS08_8000001293'],crafts['ZS08_8000001365']]),
           'ZS09':Device(id='ZS09',crafts=[crafts['ZS09_8000001365'],crafts['ZS09_8000001293']]),'ZS10':Device(id='ZS10',crafts=[crafts['ZS10_8000001293'],crafts['ZS10_8000001365']]),
           'ZS11':Device(id='ZS11',crafts=[crafts['ZS11_8000001293'],crafts['ZS11_8000001365']]),'ZS12':Device(id='ZS12',crafts=[crafts['ZS12_8000001365'],crafts['ZS12_8000001293']]),
           'ZS13':Device(id='ZS13',crafts=[crafts['ZS13_8000001365'],crafts['ZS13_8000001293']]),'ZS15':Device(id='ZS15',crafts=[crafts['ZS15_8000001365'],crafts['ZS15_8000001293']]),
           'ZS16':Device(id='ZS16',crafts=[crafts['ZS16_8000001293'],crafts['ZS16_8000001365']]),'ZS17':Device(id='ZS17',crafts=[crafts['ZS17_8000001293'],crafts['ZS17_8000001365']]),
           'ZS18':Device(id='ZS18',crafts=[crafts['ZS18_8000001365'],crafts['ZS18_8000001293']]),'ZS19':Device(id='ZS19',crafts=[crafts['ZS19_8000001293'],crafts['ZS19_8000001365']]),
           'ZS20':Device(id='ZS20',crafts=[crafts['ZS20_8000001365'],crafts['ZS20_8000001293']]),'ZS21':Device(id='ZS21',crafts=[crafts['ZS21_8000001293'],crafts['ZS21_8000001365']]),
           'ZS22':Device(id='ZS22',crafts=[crafts['ZS22_8000001365'],crafts['ZS22_8000001293']]),'ZS23':Device(id='ZS23',crafts=[crafts['ZS23_8000001293'],crafts['ZS23_8000001365']]),
           'ZS24':Device(id='ZS24',crafts=[crafts['ZS24_8000001365'],crafts['ZS24_8000001293']]),'ZS25':Device(id='ZS25',crafts=[crafts['ZS25_8000001365'],crafts['ZS25_8000001293']]),
           'ZS26':Device(id='ZS26',crafts=[crafts['ZS26_8000001293'],crafts['ZS26_8000001365']])}

# stage_names 是有序的stages.keys()， 不同任务可能需要经过不同工序
stage_names = ['HT', 'SZ', 'TS', 'ZS']
# 任务需要经过的不同工序被罗列在stages
# "stage_names": Stage("stage_names", materials=[materials[该阶段生产的物料ID]，])
stages = {
    'HT': Stage('HT', materials=[materials['8000286138']]),
    'SZ': Stage('SZ', materials=[materials['8000066422']]),
    'TS': Stage('TS', materials=[materials['8000031456']]),
    'ZS': Stage('ZS', materials=[materials['8000001293'], materials['8000001365']]),
}

# 由于可能会移除某些设备，因此，阶段设备被额外定义,这里默认将已定义的设备全部初始化
for stage in stage_names:
    stages[stage].set_devices([devices[d] for d in devices.keys() if d[:2]==stage])


def test_print():
    print('all stages')
    for s in stages:
        print(stages[s])

    print('all devices')
    for s in devices:
        print(devices[s])

    print('all crafts')
    for s in crafts:
        print(crafts[s])

    print('all materials')
    for s in materials:
        print(materials[s])

# test_print()