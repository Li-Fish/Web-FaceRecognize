import numpy as np
import io

a = np.arange(5)
out = io.BytesIO()
np.save(out, a)
out.seek(0)
data = out.read()
print(len(data))

out = io.BytesIO(data)
out.seek(0)
t = np.load(out)
print(t)
