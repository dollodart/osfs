#define _XOPEN_SOURCE 500
#define MAX_NUM_FILES 1000

#include <ftw.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>


struct stat lb;
struct stat plb;

static int
serialize(const char *fpath, const struct stat *statb,
             int tflag, struct FTW *ftwbuf)
{
  printf("%s,", fpath);
  printf("%d,", ftwbuf->level);
  lstat(fpath, &lb); // don't follow symlink


  printf("%d,", lb.st_mode);    /* protection */
  printf("%ld,", lb.st_ino);
  switch (lb.st_mode & S_IFMT) {
	case S_IFLNK:
	    stat(fpath, &plb); 
	    printf("%ld,", plb.st_ino);
	default:
	    printf("0,");
  }
  printf("%ld,", lb.st_nlink);   /* number of hard links */
  printf("%d,", lb.st_uid);     /* user ID of owner */
  printf("%d,", lb.st_gid);     /* group ID of owner */
  printf("%ld,", lb.st_rdev);    /* device ID (if special file) */
  printf("%ld,", lb.st_size);    /* total size, in bytes */
  printf("%ld,",lb.st_blksize); /* blocksize for file system I/O */
  printf("%ld,", lb.st_blocks);  /* number of blocks allocated */
  printf("%ld,", lb.st_atime);   /* time of last access */
  printf("%ld,", lb.st_mtime);   /* time of last modification */
  printf("%ld,", lb.st_ctime);   /* time of last status change */
  printf("\n");
  return 0;
}


int
main(int argc, char *argv[])
{

    int flags = 0;

    if (argc > 2 && strchr(argv[2], 'd') != NULL)
        flags |= FTW_DEPTH;
    if (argc > 2 && strchr(argv[2], 'p') != NULL)
        flags |= FTW_PHYS; // don't follow symlinks

  printf("fpath,");
  printf("level,");
  printf("st_mode,");
  printf("st_ino,");
  printf("pst_ino,");
  printf("st_nlink,");
  printf("st_uid,");
  printf("st_gi,");
  printf("st_rdev,");
  printf("st_size,");
  printf("st_blksize,");
  printf("st_blocks,");
  printf("st_atime,");
  printf("st_mtime,");
  printf("st_ctime,");
  printf("\n");

   if (nftw((argc < 2) ? "." : argv[1], serialize, 20, flags)
            == -1) {
        perror("nftw");
        exit(EXIT_FAILURE);
    }
   exit(EXIT_SUCCESS);
}
