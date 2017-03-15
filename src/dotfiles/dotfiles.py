#! /usr/bin/env python

import argparse
import logging
import os

from dot_mechanism import read_dotfile, make_private_symlinks, make_public_copies, clone_public_repo
from git_funcitons import git_commit

# Constants

DEF_DOTFILE = '.dotfile'

# Description and misc docstrings:

DESCRIPT = """
Makes symlinks to working directories and public git directories as specified
in ~/.dotfile.
"""


###########
# Logging #
###########

def logr(args):
    if args.verbose == None:
        logging.basicConfig(level=logging.ERROR)
    elif args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose >= 1:
        logging.basicConfig(level=logging.DEBUG)

    log = logging.getLogger('dotfiles')

    dir_of_this_file = os.path.dirname(__file__)
    dir_above_this_file, _ = os.path.split(dir_of_this_file)
    root_dir, _ = os.path.split(dir_above_this_file)

    log_path = root_dir + '/logs/dotfiles.log'
    print(log_path)
    fh = logging.FileHandler(log_path)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    log.addHandler(fh)
    return log


################################
# Argument and dotfile parsing #
################################

# Argparsing
def def_args():
    parser = argparse.ArgumentParser(description=DESCRIPT)
    # Define the configuration file
    parser.add_argument('-d', '--dotfile',
                        help='Define alternative dotfile for this run.')
    # Setup or backup
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--setup", action="store_true", default=False,
                       help="Sets up the dotfile system.")
    group.add_argument("--backup", action="store_true", default=False,
                       help="Does a backup on public and/or private repos.")

    # Public or private
    group_pp = parser.add_mutually_exclusive_group(required=True)
    group_pp.add_argument("--public", action="store_true", default=False,
                          help="Sets or backs up the public repository, on top of the private.")
    group_pp.add_argument("--private", action="store_true", default=False,
                          help="Sets up only the private repository.")
    # Set verbosity
    parser.add_argument('--verbose', '-v', action='count',
                        help='Increase output verbosity.')
    parser.add_argument('--no_git', action='store_true', default=False,
                        help="leaves out any git call from run.")
    return parser


def parse_cl_args():
    parser = def_args()
    args = parser.parse_args()
    return args


###############
# Usage modes #
###############

# TODO logging
def setup(args, config, log):
    """Makes symlinks from private repo to working directories for dotfiles. \
    IF public argument set, makes directory for public repo, if not present \
    clones repo, if URL present in ~/.dotfiles, copies the public files to it \
    and commit/pushes it, as if to test."""

    # Symlink
    make_private_symlinks(config["backup-folders"], config['repositories'], log)

    # Copy public files if needed
    if args.public:
        if not args.no_git:
            clone_public_repo(config)
        make_public_copies(config["backup-folders"], config['repositories'], log)


# TODO logging
def backup(args, config, log):
    """Commits every change in private repo, then commits it. IF public is set
    copies public files from private repo, to public dir, then commits and
    pushes."""
    if not args.no_git:
        git_commit(config["repositories"]["private"]["dir"],
                   "Backup made by dotfiles.")

    if args.public:
        make_public_copies(config["backup-folders"], config['repositories'], log)
        if not args.no_git:
            git_commit(config["repositories"]["public"]["dir"],
                       "Backup made by dotfiles.")


########
# Main #
########

def main():

    args = parse_cl_args()
    log = logr(args)
    log.debug(args.dotfile)
    cnf = read_dotfile(args.dotfile, DEF_DOTFILE, log)

    if not args.setup and not args.backup or not args.private and not args.public:
        print("Invalid arguments. You can get help with dotfiles -h.")
    else:
        if args.setup:
            setup(args, cnf, log)
        if args.backup:
            backup(args, cnf, log)


if __name__ == '__main__':
    main()
