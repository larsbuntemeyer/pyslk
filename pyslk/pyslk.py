"""Main module."""

import os
import subprocess
from getpass import getpass


slk_exe = '/sw/rhel6-x64/slk/slk-3.1.36/bin/slk'
decode = 'split'
format = "utf-8"


def _decode(text, mode="split", format="utf-8"):
    if mode=="split":
        split = text.decode(format).split('\n')
        return [s for s in split if s]
    return text.decode(format)


def _execute(commands):
    process = subprocess.Popen(commands,
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if (process.returncode > 0):
        raise Exception(_decode(stdout)+_decode(stderr)+
                        ['returncode: '+str(process.returncode)])
    return stdout, stderr




def _handle_output(output, decode=True):
    if output[1]:
        raise Exception(_decode(output[1]))
    if decode:
        return _decode(output[0], mode=decode)
    return output[0]


def _parse_ls(output, path=None):
    """Parsed the output from a list command.
    
    The parsing is very much static and fixed to the current
    list output of slk-3.1.36. 
    
    """
    rows = []
    for line in output:
        if line.startswith("/"):
            path = line[:-1]
        split = [entry for entry in line.split(" ") if entry]
        if len(split) == 7:
            split.insert(3, '')
        if len(split) == 8:
            # if path is a path and not a search id...
            if type(path) is str:
                split[-1] = os.path.join(path, split[-1])
            _parse_date(split)
            rows.append(split)
            #rows.append(split)
        
    return _create_df(rows)
       

def _parse_date(row):
    """parse the date of a single row into datetime object."""
    import datetime as dt
    import calendar
    day_ix = 4; mon_ix = 5; year_ix = 6;
    date = dt.date(int(row[year_ix]), 
                   list(calendar.month_abbr).index(row[mon_ix]), 
                   int(row[day_ix]))
    del row[day_ix:year_ix+1]
    row.insert(day_ix, date)
    return row
    
    
def _create_df(rows):
    """parse a single row from list output"""
    import pandas as pd
    cols = ['permissions', 'user', 'group', 'size', 'date', 'name']
    return pd.DataFrame(rows, columns=cols)
        
    
def _ls_to_pandas(output, path):
    import pandas as pd
    import numpy as np
    lines = _parse_ls(output, path)
    df = pd.DataFrame(lines)#.dropna(axis=1, how='all')
    return df.replace('', np.nan).dropna(axis=1, how='all')
       

def login(user=None, password=None):
    """Not sure how to pass user and password"""
    if user is None:
        print('Enter username:', end=' ')
        user = input().encode('utf-8')
    if password is None:
        password = getpass('Enter password for %s: ' % user)
    p = subprocess.Popen(['slk', 'login'], 
                         stdin=subprocess.PIPE, 
                         stdout=subprocess.PIPE,
                         shell=False)
    p.stdin.write()
    p.stdin.flush()
    return p.communicate()
    
    
def archive(path, target, recursive=False, exclude=True):
    """Upload files in a directory and optionally tag resources.
    
    This command transfers files and directories from the Linux device 
    to the HSM system. Appending the recursive options performs a full recursive 
    archival as `cp -r` would do. A progress indicator is shown until the 
    transfer is complete.
    When `exclude=True` is set all files and folders which names start 
    with . are ignored. All files in such folders are also ignored. 
    This helps omitting folders of your version control software or config 
    files of your system.
    
    Parameters
    ----------
    path: str
        File or directory that should be archived.
    target: str
        Target path or directory on the HSM system.
    recursive: bool
        Perform recursive archiving of subdirectories.
    exclude: bool
        Exclude hidden files and directories.
    
    """
    command = [slk_exe, "archive", path, target]
    if recursive: command.append("-R")
    output = _handle_output(_execute(command),
                            decode=decode)
    return output
    #slk archive -R /lustre_dir /tape_dir

def chmod(x):
    """Change the access mode of a resource or namespace
    """
    pass


def delete(x):
    """Soft delete a namespace (and all child objects for the
    """
    pass


def group(x):
    """Change the group of a resource or namespace
    """
    pass


def ls(path = "/", recursive = False, decode = "split"):
    """List results from search id or GNS path

    Parameters
    ----------
    path: str or int
        Search path or id.
    recursive: bool
        If True, search recursively.
    decode: str
        Decode mode, can either be True, \"split\" or \"pandas\".

    Returns
    -------
    Search results.

    """
    command = [slk_exe, "list", str(path)]
    if recursive: command.append("-R")
    output = _handle_output(_execute(command),
                            decode=decode)
    if decode == 'pandas':
        return _ls_to_pandas(output.split('\n'), path)
    return output


def move():
    """Move namespaces/files from one parent folder to another
    """
    pass


def owner(x):
    """Change the owner of a resource or namespace
    """
    pass


def rename():
    """Rename a folder or file
    """
    pass


def retrieve(path, target=".", recursive=False):
    """Download files for search and start WFE jobs for 
    files on tape using search id or GNS path
    
    Parameters
    ----------
    path: str
        File or directory that should be retrieved.
    target: str
        Target path or directory on the file system.
    recursive: bool
        Perform recursive archiving of subdirectories.
    
    """
    command = [slk_exe, "retrieve", str(path), target]
    if recursive: command.append("-R")
    output =  _handle_output(_execute(command), decode='split')
    if output: 
        return output



def search(group=None, name=None, user=None, out='ls', decode='split'):
    """Creates search and returns search id
    
    Parameters
    ----------
    group: str
         group attribute to search.
    name: str
         filename to search.
    user: str
         user id to search.
    out: str
         Output format, can either be `ls` or `id`.
    decode: str
         Output format if `ls` is used, can be `split` or `pandas`.
         
    Returns
    -------
    
    Search ID or list result depending on out attribute.
    
    """
    command = [slk_exe, "search"]
    if group:
        command.extend(["-group", group])
    if name:
        command.extend(["-name", name])
    if user:
        command.extend(["-user", user])
    output = _handle_output(_execute(command),
                            decode="split")
    # parse output into integer search id
    ID = int(output[0].split(":")[1])
    if out == 'ls':
        return ls(ID, decode=decode)
    elif out == 'id':
        return ID
    return ID


def tag(x):
    """Apply metadata to the namespace and child resources
    """
    pass
