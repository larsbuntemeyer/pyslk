"""Main module."""

import os
import subprocess


slk_exe = '/sw/rhel6-x64/slk/slk-3.1.36/bin/slk'
to_pandas = False


def _decode(text, mode="split", format="utf-8"):
    if mode=="split":
        return text.decode(format).split('\n')
    return text.decode(format)


def _execute(commands):
    process = subprocess.Popen(commands,
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if (process.returncode > 0):
        raise Exception(_decode(stdout)+_decode(stderr))
    return stdout, stderr


#def execute(command):
#    return subprocess.check_call(command)

def login():
    return execute([slk_exe, "login"])

def test():
    return decode(execute([slk_exe])[0])


def user():
    p = subprocess.Popen(['slk', 'login'], 
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return p.communicate(input='')


def _handle_output(output, decode=True):
    if output[1]:
        raise Exception(_decode(output[1]))
    if decode:
        return _decode(output[0], mode=decode)
    return output[0]


def _decode_ls(output, path=""):
    """decode a filesystem output"""
    rows = []
    for line in output:
        if line.startswith("/"):
            path = line[:-1]
        split = [entry for entry in line.split(" ") if entry]
        if len(split) == 7:
            split.insert(3, '')
        if len(split) == 8:
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
    lines = _decode_ls(output, path)
    df = pd.DataFrame(lines)#.dropna(axis=1, how='all')
    return df.replace('', np.nan).dropna(axis=1, how='all')
       

def archive(x):
    """Upload files in a directory and optionally tag resources
    """
    pass


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
    """
    command = [slk_exe, "list", path]
    if recursive: command.append("-R")
    output = _handle_output(_execute(command),
                            decode=decode)
    if decode == 'pandas':
        return _ls_to_pandas(output.split('\n'), path)
    return output


def login():
    """Login using your LDAP username and password
    """
    pass


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


def retrieve(x):
    """Download files for search and start WFE jobs for files on
    """
    pass


def search(x):
    """Creates search and returns search id
    """
    pass


def tag(x):
    """Apply metadata to the namespace and child resources
    """
    pass