from git import Repo
import pandas as pd
import sys
import os
import re

class FunctionChangeObserver():
    def __init__(self, repository):
        dir_array = repository.split('/')
        dir_name = dir_array[len(dir_array) - 1]
        self.functional_regex = re.compile("(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])")
        self.csv_dict = {
            "Commit SHA": [],
            "Java File": [],
            "Old Function Signature": [],
            "New Function Signature": []
        }
        if os.path.isdir(dir_name):
            self.repo = Repo(dir_name + '/.git')
        else:
            repo = Repo('.git')
            repo.git.clone(repository)
            self.repo = Repo(dir_name + '/.git')

    def get_all_commits(self):
        all_commits = list(self.repo.iter_commits('master'))
        return all_commits

    def process_all_commits(self):
        all_commits = self.get_all_commits()
        for index in reversed(range(1, len(all_commits))):
            old_commit = all_commits[index-1]
            new_commit = all_commits[index]
            modified_diff = self.get_modified_commit_diff(old_commit, new_commit)
            if modified_diff is not None and len(modified_diff) > 0:
                functional_diff = self.get_functional_changes(modified_diff)
                if len(functional_diff) > 0:
                    self.add_to_csv(functional_diff, new_commit.hexsha)
        df = pd.DataFrame(self.csv_dict)
        df.to_csv('data.csv', index=None)

    def get_modified_commit_diff(self, old_commit, new_commit):
        diff = self.repo.git.diff(old_commit, new_commit)
        diff_array = diff.split('\n')
        index = 0
        modified = []
        while index < len(diff_array) - 1:
            if diff_array[index].startswith('-') and diff_array[index + 1].startswith('+'):
                modified.append(diff_array[index])
                modified.append(diff_array[index + 1])
                index += 2
                continue
            index += 1
        if len(modified) > 0:
            change_dict = self.convert_change_list_to_dict(modified)
            only_java_changes = self.remove_non_java_and_empty_files(change_dict)
        else:
            return None
        return only_java_changes

    def convert_change_list_to_dict(self, modified_list):
        changes_dict = {}
        file_name = ""
        for index in range(0, len(modified_list), 2):
            old = modified_list[index]
            new = modified_list[index+1]
            if old.startswith('--- '):
                file_name = old.split()[1][2:]
                changes_dict[file_name] = []
            else:
                changes_dict[file_name].append(old)
                changes_dict[file_name].append(new)
        return changes_dict

    def remove_non_java_and_empty_files(self, change_dict):
        file_names = change_dict.keys()
        new_dict = {}
        for file in file_names:
            if file.find('.java') > -1 and len(change_dict[file]) > 0:
                new_dict[file] = change_dict[file]
        return new_dict

    def get_functional_changes(self, diff_dict):
        new_dict = {}
        for file_name in diff_dict.keys():
            for index in range(0, len(diff_dict[file_name]), 2):
                deletion = diff_dict[file_name][index]
                addition = diff_dict[file_name][index + 1]
                is_function = self.functional_regex.search(deletion) and self.functional_regex.search(addition)
                if is_function is not None and len(deletion.split(',')) < len(addition.split(',')):
                    if file_name in new_dict:
                        new_dict[file_name].append(deletion)
                        new_dict[file_name].append(addition)
                    else:
                        new_dict[file_name] = [deletion, addition]
        return new_dict

    def add_to_csv(self, diff_dict, commit_hash):
        for file_name in diff_dict.keys():
            for index in range(0, len(diff_dict[file_name]), 2):
                old = diff_dict[file_name][index]
                new = diff_dict[file_name][index + 1]
                old_signature = self.get_function_signature(old)
                new_signature = self.get_function_signature(new)
                self.csv_dict["Commit SHA"].append(commit_hash)
                self.csv_dict["Java File"].append(file_name)
                self.csv_dict["Old Function Signature"].append(old_signature)
                self.csv_dict["New Function Signature"].append(new_signature)

    def get_function_signature(self, change):
        find = re.search('\s+\w+\([^\)]*\)*', change)
        signature = find.group(0)
        return signature.strip()


fc = FunctionChangeObserver("https://github.com/JakeWharton/RxRelay")
fc.process_all_commits()