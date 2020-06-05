#! /bin/bash



for tui in 100 200 800
do
    python3 run.py --cuda --gpus 0  --gamma 0.99 --lr 0.001  --nEpochs 4 --tui $tui &
done