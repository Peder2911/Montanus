# A function pair that is equivalent to the open() function and file object.
# used to easily give utilities DFI compatibility.

import redis

class RedisFile():
    """
    An object mimicing a file, but writing to and reading from a redis list.
    Entries in the list are rows, separated by newline.

    This makes it easier to write scripts for DFI that are compatible with
    both files, and the DB.

    Remember that this object pops objects from the list.
    """
    def __init__(self,listkey,**kwargs):
        self.r = redis.Redis(**kwargs)
        self.listkey = listkey

    def write(self,data):
        for ln in data.split('\n'):
            linesWrote = self.r.rpush(self.listkey,ln)

    def read(self):
        val = ''
        res = []

        while val is not None:
            if val != '':
                res.append(val.decode())
            val = self.r.lpop(self.listkey)

        res = '\n'.join(res)
        return(res)

    def __enter__(self):
        pass

    def __exit__(self,exc_type,exc_value,traceback):
        pass
