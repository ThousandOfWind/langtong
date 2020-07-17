#! /bin/bash


python3 run.py --cuda --gpus 0 --batchSize 32 --rewardType se2 --obStyle primitive --agentType RL  --obId --fakeOBTL 200&
python3 run.py --cuda --gpus 0 --batchSize 32 --rewardType se2 --obStyle primitive --agentType RL  &
python3 meanfield.py --cuda --gpus 0 --batchSize 32 --rewardType se2 --obStyle lstm --agentType MF  --obId --curriculum&
python3 meanfield.py --cuda --gpus 0 --batchSize 32 --rewardType se2 --obStyle lstm --agentType MF  &
python3 meanfield.py --cuda --gpus 0 --batchSize 32 --rewardType se2 --obStyle primitive --agentType MF  &
python3 meanfield.py --cuda --gpus 0 --batchSize 32 --rewardType se2 --obStyle primitive --agentType MF-RNN  &
