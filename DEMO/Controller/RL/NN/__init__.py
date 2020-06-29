from .model import DNNAgent as DNN
from .seqLSTM import DNNAgent as seqLSTM
from .mfbase import DNNAgent as MF

NN = {
    'DNN': DNN,
    'seqLSTM': seqLSTM,
    'MF': MF,
}
