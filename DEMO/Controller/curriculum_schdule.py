import numpy as np

e = np.eye(6)

BASE_CUR = [(e[i], 1) for i in range(6)]

BASE2_CUR = [(e[i], 0.5) for i in range(6)] + [(e[i], 1) for i in range(6)]


CURs = {
    'base': BASE_CUR,
    'base2': BASE2_CUR,
}