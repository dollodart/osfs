import os
from stat import (S_IMODE, S_IFMT,
                  S_IFDIR, S_IFCHR,
                  S_IFBLK, S_IFREG,
                  S_IFIFO, S_IFLNK,
                  S_IFSOCK)

class File():
    total_dir = dict()
    total_inode_dir = dict()

    def __init__(self, parent, name, st):
        self.parent = parent
        self.name = name
        self.st = st

        path = []
        parent = self.parent
        while parent is not None:
            name = parent.name
            path.append(name)
            parent = parent.parent
        path = list(reversed(path))
        path.append(self.name)
        self.path = '/'.join(path)

        self.__class__.total_dir[self.path] = self
        self.__class__.total_inode_dir[self.st.st_ino] = self

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
            return File.total_inode_dir[self.st.pst_ino]
        except (KeyError, AttributeError) as e:
            try:
                return File.total_inode_dir[os.stat(self.absolute()).st_ino]
            except (KeyError, FileNotFoundError, PermissionError) as e:
                return None
        except (FileNotFoundError, PermissionError) as e:
            pass

class Mount(File):
    iter_order = 0
    pass

class BlockDevice(File):
    iter_order = 0
    pass

class CharDevice(File):
    iter_order = 0
    pass

class Socket(File):
    iter_order = 0
    pass

factorydct = {
        S_IFDIR: Directory,
        S_IFREG: RegularFile,
        S_IFLNK: SymLink,
        S_IFBLK: BlockDevice,
        S_IFCHR: CharDevice,
        S_IFSOCK: Socket}
