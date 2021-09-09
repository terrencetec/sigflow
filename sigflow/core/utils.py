import numpy as np

def to_array(value, types=None):
    """Converts value to a list of values
    while checking the type of value.

    Parameters
    ----------
    value :
        The value to convert from.
    types : class or tuple of class, optional
        Value types which are allowed to be.
        Defaults to None, meaning no type checking is performed.

    Returns
    -------
    list
        value converted as list of values
    """
    value = np.atleast_1d(value)

    if types is not None:
        for val in value:
            if not isinstance(val, types):
                raise TypeError("expected value's type %s\nactual type %s"
                                % (str(types),  str(val.__class__.__name__)))
    return value




