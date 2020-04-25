import numpy as np
import io


def array_to_bin(data):
    out = io.BytesIO()
    np.save(out, data)
    out.seek(0)
    return out.read()


def bin_to_array(data):
    out = io.BytesIO(data)
    out.seek(0)
    return np.load(out)
