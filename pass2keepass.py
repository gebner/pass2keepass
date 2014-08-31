#!/usr/bin/env python
from kppy.database import KPDBv1
import fnmatch, os, subprocess, getpass

pass_store_dir = os.path.expanduser('~/.password-store/')
keys = [ os.path.join(dirpath, fn)[len(pass_store_dir):-4]
        for dirpath, dirnames, files in os.walk(pass_store_dir)
        for fn in files if fn.endswith('.gpg')]

db = KPDBv1(new=True)

kpgroups = {}

def get_group(db, parent, kpgs, group_names):
    group_name = group_names[0]
    if group_name in kpgs:
        kpgroup = kpgs[group_name][0]
    else:
        db.create_group(group_name, parent)

        # WTF API design???
        if parent == None:
            kpgroup = db.groups[-1]
        else:
            kpgroup = parent.children[-1]

        kpgs[group_name] = (kpgroup, {})

    if len(group_names) == 1:
        return kpgroup
    else:
        return get_group(db, kpgroup, kpgs[group_name][1], group_names[1:])

for key in keys:
    cont = subprocess.check_output(['pass', 'show', key]).decode()
    groups = key.split('/')
    basename = groups.pop()

    kpgroup = get_group(db, None, kpgroups, groups)

    passwd, rest = cont.split('\n', 1)
    url = ''
    username = ''
    comments = []
    for line in rest.split('\n'):
        if line.startswith('url: '):
            url = line[len('url: '):]
        elif line.startswith('username: '):
            url = line[len('username: '):]
        else:
            comments.append(line)

    kpgroup.create_entry(basename, url=url, username=username, password=passwd, comment='\n'.join(comments))

db.remove_group(db.groups[0]) # Internet group
db.save('pass-store.kdb', getpass.getpass('password for pass-store.kdb: '))
db.close()
