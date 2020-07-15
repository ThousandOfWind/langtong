#! /bin/bash


python3 meanfield.py --cuda --gpus 1 --batchSize 32 --rewardType se2 --obStyle lstm --agentType MF  --obId --curriculum&
python3 meanfield.py --cuda --gpus 1 --batchSize 32 --rewardType se2 --obStyle lstm --agentType MF  &


python3 meanfield.py --cuda --gpus 2 --batchSize 32 --rewardType se2 --obStyle primitive --agentType MF  --obId --curriculum&
python3 meanfield.py --cuda --gpus 2 --batchSize 32 --rewardType se2 --obStyle primitive --agentType MF  &

python3 meanfield.py --cuda --gpus 3 --batchSize 32 --rewardType se2 --obStyle primitive --agentType MF-RNN  --obId --curriculum&
python3 meanfield.py --cuda --gpus 3 --batchSize 32 --rewardType se2 --obStyle primitive --agentType MF-RNN  &

python3 run.py --cuda --gpus 0 --batchSize 32 --rewardType se2 --obStyle primitive --agentType RL  --obId --fakeOBTL 500&
python3 run.py --cuda --gpus 0 --batchSize 32 --rewardType se2 --obStyle primitive --agentType RL  &