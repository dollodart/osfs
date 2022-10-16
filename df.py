import pandas as pd
import matplotlib.pyplot as plt
from stat import *

def read_df(filename):
    with open(filename, 'r') as _:
        df = pd.read_csv(_,header=0,on_bad_lines='warn')
    return df


def dist_file_types(df):
    st_mode = df['st_mode'].value_counts()
    dct = {
            S_IFDIR: 'Directory',
            S_IFREG: 'RegularFile',
            S_IFLNK: 'SymLink',
            S_IFBLK: 'BlockDevice',
            S_IFCHR: 'CharDevice',
            S_IFSOCK: 'Socket'}
    st_mode.index = st_mode.index.map(S_IFMT).map(dct)
    return st_mode.groupby(level=0).sum().sort_values()


def dist_depths(df):
    plt.figure()
    plt.plot(range(len(df)), df['level'].sort_values())
    print(df['level'].value_counts()) # table for discrete valued field
    return None

def dist_times(df):
    plt.figure()
    for y in 'st_atime', 'st_mtime', 'st_ctime':
        y2 = df[y].map(datetime.utcfromtimestamp)
        plt.plot(range(len(y2)), sorted(y2), label=y)
    plt.legend()
    return None

def dist_sizes(df):
    plt.figure()
    plt.plot([x/len(df) for x in range(len(df))], sorted(df['st_size']))
    iqr = df['st_size'].quantile(.75) - df['st_size'].quantile(.25)
    plt.ylim(df['st_size'].quantile(.5) - 3*iqr, df['st_size'].quantile(.5) + 3*iqr)
    return None

def corr_size_nlinks(df):
    plt.figure()
    bl = df['st_size'] <= 4096 # for directories and smaller files
    plt.scatter(df[bl]['st_nlink'], df[bl]['st_size'])
    return None

if __name__ == '__main__':
    df = read_df('filesystem')
    print(dist_file_types(df))
