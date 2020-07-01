#! /bin/bash

python3 curriculum.py --cuda --gpus 0 --batchSize 32 --rewardType se2 --obStyle lstm&
python3 curriculum.py --cuda --gpus 0 --batchSize 32 --etl 150 --tui 200 --rewardType se2 --obStyle lstm&

python3 curriculum.py --cuda --gpus 1 --batchSize 32 --curriculumMemory share --rewardType se2 --obStyle lstm&
python3 curriculum.py --cuda --gpus 1 --batchSize 32 --rewardType se2 --obStyle primitive&

python3 curriculum.py --cuda --gpus 2 --batchSize 32 --rewardType se2 --obStyle concat&
python3 curriculum.py --cuda --gpus 2 --batchSize 32 --curriculumStyle base2 --rewardType se2 --obStyle lstm&

python3 run.py --cuda --gpus 3 --batchSize 32 --rewardType se2 --obStyle lstm&
python3 run.py --cuda --gpus 3 --batchSize 32 --rewardType se2 --obStyle primitive&
python3 run.py --cuda --gpus 3 --batchSize 32 --rewardType se2 --obStyle concat&


python3 curriculum.py --cuda --gpus 0 --curriculumTL 400 --batchSize 32 --etl 150 --tui 200 --rewardType se2 --obStyle lstm&
python3 curriculum.py --cuda --gpus 1 --curriculumTL 400 --batchSize 32 --etl 150 --tui 150 --rewardType se2 --obStyle lstm&


python3 meanfield.py --cuda --gpus 1 --batchSize 32 --mamorySize 40 --rewardType se2 &
python3 meanfield.py --cuda --gpus 1 --batchSize 32 --mamorySize 40 --rewardType step &


python3 meanfield.py --cuda --gpus 2 --batchSize 32 --rewardType se2 --obStyle lstm --obId&
