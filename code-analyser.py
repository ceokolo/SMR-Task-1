from git import Repo
from git.compat import defenc
import difflib
import sys

repo = Repo('.git')
all_commits = list(repo.iter_commits('master'))
for commit in all_commits:
    print(commit.message, commit.hexsha)

i = 0
while i < len(all_commits) - 1:
    diff = repo.git.diff(all_commits[i+1], all_commits[i])
    diff_array = diff.split('\n')
    j = 0
    modified = []
    while j < len(diff_array) - 1:
        if diff_array[j].startswith('-') and diff_array[j + 1].startswith('+'):
            modified.append(diff_array[j])
            modified.append(diff_array[j + 1])
            j += 2
            continue
        j += 1
    print("\n".join(modified))
    """for change in all_commits[i].diff(all_commits[i + 1]).iter_change_type('M'):
        first = change.a_blob.data_stream.read().decode('utf-8')
        second = change.b_blob.data_stream.read().decode('utf-8')
        print(list(difflib.unified_diff(first, second)))"""
    print("======================================================\n")
    i += 1