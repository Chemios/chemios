from chemiosbrain.utils import make_json_compatible
import numpy as np
import json

data = {'x': np.int64(3), 'y': {'z': np.array([1,2,3]), 'w': [1,2,3]}}
update = make_json_compatible(data)
print(json.dumps(update))

