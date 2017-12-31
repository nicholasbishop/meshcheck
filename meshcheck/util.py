"""Common code that doesn't fit elsewhere."""


def to_gl(mat):
    return mat.value.tobytes()
