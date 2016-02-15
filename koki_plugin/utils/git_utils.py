import subprocess

def git_diff(from_head=0, to_head=1):
    cmd = ["git", "diff", "--name-status", "HEAD~" + str(from_head), "HEAD~" + str(to_head)]
    diff_list = subprocess.check_output(cmd, universal_newlines=True).split("\n")
    return diff_list

def git_log():
    cmd = ["git", "log", "--stat"]
    log_list = subprocess.check_output(cmd, universal_newlines=True)
    commit_block = _make_commit_block(log_list)
    return commit_block

def _make_commit_block(log):
    lines = log.splitlines()
    commit_block = []
    temp = []
    for line in lines:
        if "commit" in line:
            if temp != []:
                commit_block.append(temp)
            temp = []
        temp.append(line)

    return commit_block
