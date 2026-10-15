"""Pinned Blender glTF corner-normal conversion for independent source checks.

The installed exporter rounds local float32 normals to four decimal places,
normalizes, replaces zero with local +Z, then changes axes. It is NOT a normal
accessor quantization: glTF NORMAL remains FLOAT (5126). Reproduce that declared
conversion before inverse-transpose, rather than loosening a world-space error
threshold. Actual prebatch/runtime accessor comparisons remain independent.
"""
import math
import numpy as np
from mathutils import Vector

ROUNDING_DIGITS = 4
# Bound the supported FP32 transform class, never widen a normal comparison.
# gamma_3 * 64 ~= 1.15e-5, below the fixed 2e-5 attribute comparison budget;
# reserve the remaining budget for normalization/TRS serialization rounding.
MAX_CONDITION = 64.0
# Half a decimal quantization step plus conservative float32 input/round error.
LOCAL_VECTOR_ERROR = math.sqrt(3) * (0.5 * 10**-ROUNDING_DIGITS + 2**-22)


def canonical_array(local):
    value=np.round(np.asarray(local,dtype=np.float32),ROUNDING_DIGITS)
    lengths=np.linalg.norm(value,axis=1,keepdims=True)
    np.divide(value,lengths,out=value,where=lengths!=0)
    value[~value.any(axis=1),2]=1
    return value


def canonical(local):
    return Vector(tuple(float(v) for v in canonical_array([local])[0]))


def condition_and_bound(matrix):
    values=np.asarray(matrix.to_3x3(),dtype=np.float64)
    singular=np.linalg.svd(values,compute_uv=False)
    condition=float(singular[0]/singular[-1]) if singular[-1]>0 else math.inf
    if not math.isfinite(condition) or condition>MAX_CONDITION*(1+1e-6):
        raise ValueError(f'Unsupported ill-conditioned source normal transform: {condition}')
    rho=condition*LOCAL_VECTOR_ERROR
    chord=2*rho/(1-rho)
    return condition,chord,math.degrees(2*math.asin(min(1,chord/2)))
