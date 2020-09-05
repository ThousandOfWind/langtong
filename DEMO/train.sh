#! /bin/bash



python3 meanfield.py --cuda --gpus 0 --batchSize 32 --rewardType pc --obStyle lstm --agentType RL  --obId --curriculum&
python3 meanfield.py --cuda --gpus 0 --batchSize 32 --rewardType pc --obStyle lstm --agentType MF  &
python3 meanfield.py --cuda --gpus 0 --batchSize 32 --rewardType pc --obStyle primitive --agentType MF  &
python3 meanfield.py --cuda --gpus 0 --batchSize 32 --rewardType pc --obStyle primitive --agentType MF-RNN  &


python3 meanfield.py --obStyle primitive --agentType RL --nEpisode 1000  --cuda --gpus 2 --batchSize 32  --lr 1e-4 --etl 500 --rewardType pc &
python3 meanfield.py --obStyle primitive --agentType RL --nEpisode 1000  --cuda --gpus 2 --batchSize 32  --lr 1e-4 --etl 100 --rewardType pc &
python3 meanfield.py --obStyle primitive --agentType RL --nEpisode 1000  --cuda --gpus 2 --batchSize 32  --lr 1e-4 --etl 20 --rewardType pc &


python3 meanfield.py --obStyle lstm --agentType RL --nEpisode 1000  --cuda --gpus 1 --batchSize 32  --lr 1e-4 --etl 500 --rewardType pc &
python3 meanfield.py --obStyle lstm --agentType RL --nEpisode 1000  --cuda --gpus 1 --batchSize 32  --lr 1e-4 --etl 100 --rewardType pc &
python3 meanfield.py --obStyle lstm --agentType RL --nEpisode 1000  --cuda --gpus 1 --batchSize 32  --lr 1e-4 --etl 20 --rewardType pc &

python3 meanfield.py --obStyle primitive --agentType MF2 --nEpisode 1000  --cuda --gpus 0 --batchSize 32  --lr 1e-4 --etl 500 --rewardType pc &
python3 meanfield.py --obStyle primitive --agentType MF2 --nEpisode 1000  --cuda --gpus 0 --batchSize 32  --lr 1e-4 --etl 100 --rewardType pc &
python3 meanfield.py --obStyle primitive --agentType MF2 --nEpisode 1000  --cuda --gpus 0 --batchSize 32  --lr 1e-4 --etl 20 --rewardType pc &
