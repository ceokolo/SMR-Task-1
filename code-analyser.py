from git import Repo
from git.compat import defenc
import difflib
import sys

repo = Repo('.git')
all_commits = list(repo.iter_commits('master'))
for commit in all_commits:
    print(commit.message, commit.hexsha)

i = 0
while i < len(all_commits):
    if i == len(all_commits) - 1:
        break
    print(repo.git.diff(all_commits[i+1], all_commits[i]))
    """for change in all_commits[i].diff(all_commits[i + 1]).iter_change_type('M'):
        first = change.a_blob.data_stream.read().decode('utf-8')
        second = change.b_blob.data_stream.read().decode('utf-8')
        print(list(difflib.unified_diff(first, second)))"""
    print("======================================================")
    i += 1