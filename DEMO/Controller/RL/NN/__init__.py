from .model import DNNAgent as DNN
from .seqLSTM import DNNAgent as seqLSTM
from .mfbase import DNNAgent as MF
from .mfbase_rnn import DNNAgent as MF_RNN

NN = {
    'DNN': DNN,
    'seqLSTM': seqLSTM,
    'MF': MF,
    'MF-RNN': MF_RNN,
}
