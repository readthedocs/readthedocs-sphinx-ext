from __future__ import print_function

import uuid
import nilsimsa

NILSIMSA_LIMIT = 70


def hash_node(node, obj=False):
    source = node.rawsource or node.astext()

    if obj:
        return nilsimsa.Nilsimsa(source)

    try:
        ret = u'nil-{hash}'.format(hash=nilsimsa.Nilsimsa(source).hexdigest())
    except UnicodeEncodeError:
        ret = u'uuid-{hash}'.format(hash=str(uuid.uuid1()))
    return ret


def compare_hash(hash_obj, hash_list, limit=NILSIMSA_LIMIT, allow_multiple=True):
    """
    Compare a hash to a list of existing hashes.
    Return the existing hash that most matches our new hash.
    """
    top = {0: None}
    for node_hash in hash_list:
        if not node_hash.startswith('nil'):
            continue
        nim_hash = node_hash.split('-')[-1]
        difference = hash_obj.compare(nim_hash, True)
        if difference > limit:
            # Node is the same
            top[difference] = node_hash
            print("[Commenting] Close hash found: %s %s" % (nim_hash, difference))
        else:
            pass
    if len(top) > 2:
        if allow_multiple:
            print('[Commenting] Multiple nodes match. Returning top node, but it might be wrong!')
        else:
            raise IndexError('[Commenting] Multiple nodes match. Perhaps raise your limit?')
    top_diff = sorted(top)[-1]
    return top[top_diff]
