# Dictionary utilities

def list_of_pairs_to_dict(list_of_pairs):
    '''
    Convert a list of pairs (x, y) into a dictionary.
    :param list_of_pairs: List of pairs (x, y)
    :return:
    '''
    res = {}
    for (x, y) in list_of_pairs:
        res[x] = y
    return res


def get_ordered_keys(d, order_by_value=False, reverse=False):
    '''
    Get an ordered vector containing the keys of a dictionary.
    :param dict:
    :param order_by_value: If False, sorting is made with respect to the values of the keys.
    If True, sorting is made with respect to the values of the dictionary.
    :param inverse: Inverse ordering (default False)
    :return:
    '''
    if order_by_value:
#        d_aux = {}
#        for x in d.keys():
#            d_aux[d[x]] = x
#        ordered_values = sorted(d.values(), reverse=reverse)
#        res = [d_aux[v] for v in ordered_values]
#        return res
        d_aux = {}
        for k,v in d.items():
            if v not in d_aux:
                d_aux[v] = []
            d_aux[v].append(k)
        ordered_values = sorted(d_aux.keys(), reverse=reverse)
        res = [d_aux[v] for v in ordered_values]
        return res
    else:
        return sorted(d.keys(), reverse=reverse)


def get_ordered_values(dict, order_by_key=False):
    '''
    Get an ordered vector containing the values of a dictionary.
    :param dict:
    :param order_by_keys: If False, sorting is made with respect to the values of the values.
    If True, sorting is made with respect to the keys of the dictionary.
    :return:
    '''
    if order_by_key:
        ordered_keys = sorted(dict.keys())
        res = [dict[k] for k in ordered_keys]
        return res
    else:
        return sorted(dict.values())


def flip_dict_keys_2(d):
    """
    Transforms this dictionary structure:
    {k_i: {k'j: vj}}

    into this:
    {k'j: {ki: vj}}

    :param d: The dictionary to transform.
    :return:
    """
    res = {}
    for k_i in d.keys():
        for k_j in d[k_i].keys():
            if not k_j in res.keys():
                res[k_j] = {}
            d_k_j = res[k_j]
            d_k_j[k_i] = d[k_i][k_j]
    return res


def stringifyKeys(d):
    """
    Conver to string every key contained in a dictionary. This is useful as a first step to convert a dictionary to
    JSON format.
    :param d:
    :return:
    """
    if type(d) <> dict:
        # No dictionary. Return same object.
        return d
    res = {}
    for k in d.keys():
        res[unicode(k)] = stringifyKeys(d[k])
    return res
