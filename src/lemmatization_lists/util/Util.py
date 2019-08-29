import sys
import pickle

def print_dict(obj, nested_level=0, output=sys.stdout):
    '''
    Prints a dictionary with the correct representation of utf-8 characters.
    :param obj: The dictionary to print.
    :param nested_level: This parameter is there to be able to access the nested levels
    in recursive calls.
    :param output: Where to print the output (default sys.stdout).
    '''
    spacing = '   '
    if type(obj) == dict:
        print >> output, '%s{' % ((nested_level) * spacing)
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print >> output, '%s%s:' % ((nested_level + 1) * spacing, k)
                print_dict(v, nested_level + 1, output)
            else:
                print >> output, '%s%s: %s' % ((nested_level + 1) * spacing, k, v)
        print >> output, '%s}' % (nested_level * spacing)
    elif type(obj) == list:
        print >> output, '%s[' % ((nested_level) * spacing)
        for v in obj:
            if hasattr(v, '__iter__'):
                print_dict(v, nested_level + 1, output)
            else:
                print >> output, '%s%s' % ((nested_level + 1) * spacing, v)
        print >> output, '%s]' % ((nested_level) * spacing)
    else:
        print >> output, '%s%s' % (nested_level * spacing, obj)



def save_object_to_pickle(obj, path):
    """
    Serialize a Python objecto into a pickle file.

    Args:
        - obj: The object to be serilized.
        - path: The path of the file to store the serialized object.

    Return:
        None
    """
    with open(path, "w") as f:
        pickle.dump(obj, f)


def load_object_from_pickle(path):
    """
    Read from disk and deserialize a a previously serialized object with pickle.

    Args:
        - path: The path of the file to read from.

    Return:
        The Python deserialized object.
    """
    with open(path, "r") as f:
        return pickle.load(f)


