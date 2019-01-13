from git import Repo

repo = Repo('.git')
all_commits = list(repo.iter_commits('master'))
for commit in all_commits:
    print(commit.message, commit.hexsha)

i = 0
while i < len(all_commits):
    if i == len(all_commits) - 1:
        break
    for change in all_commits[i].diff(all_commits[i + 1]).iter_change_type('M'):
        #print(change.a_blob.data_stream.read().decode('utf-8'))
        #print(change.b_blob.data_stream.read().decode('utf-8'))
        print(change)
    i += 1