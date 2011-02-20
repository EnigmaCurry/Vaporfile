import os
import hashlib
import json
import copy

def md5_for_file(path, block_size=2**20):
    md5 = hashlib.md5()
    with open(path) as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def mkdir(newdir):
    """works the way a good mkdir should :)
    - already exists, silently complete
    - regular file in the way, raise an exception
    - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                          "dir, '{0}', already exists.".format(newdir))
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        #print "mkdir {0}.format(repr(newdir))
        if tail:
            os.mkdir(newdir)

class JSONEncodable(object):
    """An inheritance mixin to make a class encodable to JSON"""
    def to_dict(self):
        d = copy.copy(self.__dict__)
        for key,value in d.items():
            if hasattr(value,"to_dict"):
                d[key] = value.to_dict()
        return d
    def to_json(self):
        return json.dumps(self.to_dict(),sort_keys=True,indent=4)
