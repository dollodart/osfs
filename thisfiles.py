import os
from stat import (S_IMODE, S_IFMT,
                  S_IFDIR, S_IFCHR,
                  S_IFBLK, S_IFREG,
                  S_IFIFO, S_IFLNK,
                  S_IFSOCK)

class File():
    total_dir = dict()

    def __init__(self, parent, name, st):
        self.parent = parent
        self.name = name
        self.st = st
        self.__class__.total_dir[st.st_ino] = self

        # attributes used for LCA algorithm
        self.rank = None
        self.p = None
        self.ancestor = None
        self.visited = None

    def absolute(self):
        s = self.name
        v = self
        while v.parent is not None:
            s = v.parent.name + '/' + s
            v = v.parent
        return s

    def __str__(self):
        return str(type(self)).split('.')[-1].rstrip('\'>') + '-' + self.absolute()

class Directory(File):
    iter_order = 1
    def __init__(self, parent, name, st):
        super().__init__(parent, name, st)
        self.children = []
    def add_child(self, child):
        self.children.append(child)

class RegularFile(File):
    iter_order = 0
    pass

class SymLink(File):
    iter_order = 2
    def points_to(self):
        try:
            return File.total_dir[os.stat(self.absolute()).st_ino]
        except (KeyError, FileNotFoundError):
            return None

class Mount(File):
    pass

class BlockDevice(File):
    pass

class CharDevice(File):
    pass

class Socket(File):
    pass

factorydct = {
        S_IFDIR: Directory,
        S_IFREG: RegularFile,
        S_IFLNK: SymLink,
        S_IFBLK: BlockDevice,
        S_IFCHR: CharDevice,
        S_IFSOCK: Socket}
