import json
import os

from koki_plugin.utils.git_utils import git_diff, git_log, is_inside_repo, git_get_root_path

PLUGIN_METADATA_PATH = os.path.dirname(__file__) + "/.data"
METADATA_FILE = "/myinfo.json"

class Koki(object):

    def __init__(self, vim):
        self.vim = vim

    def project_command_completion(self):
        projects = self._read_json(METADATA_FILE)
        if projects is None:
            return []
        else:
            return projects["projects"]

    def project_command(self, project_name):
        project_path = self.vim.command_output("echo expand('%:p:h')").split("\n")[1]
        project_name = project_name
        projects = self._read_json(METADATA_FILE)
        if project_name in projects["projects"]:
            # open project as it was
            return
        else:
            # check if its a git repo
            projects[project_name] = {"project_path": project_path, "tags": ""}
            projects["projects"].append(project_name)
            if is_inside_repo():
                project_git_root_path = git_get_root_path()
                projects[project_name].update({"git_root_path": project_git_root_path})
            self._write_to_json(projects, METADATA_FILE)

    def diff_command(self):
        diff_list = git_diff()
        self._new_scratch_buffer()
        self.vim.current.buffer[:] = diff_list

    def log_command(self):
        self._new_scratch_buffer()
        log_list = git_log()
        # TODO show appropriate message
        self.vim.current.buffer[:] = log_list[0]


    def _write_to_json(self, dict, filename):
        with open(PLUGIN_METADATA_PATH + filename, "w") as fd:
            json.dump(dict, fd, indent=4)

    def _read_json(self, filename):
        with (open(PLUGIN_METADATA_PATH + filename, "r")) as fd:
            try:
                json_object = json.load(fd)
            except ValueError:
                json_object = None
        return json_object

    def _new_scratch_buffer(self):
        self.vim.command("tabnew")
        self.vim.command("setlocal buftype=nofile")
        self.vim.command("setlocal bufhidden=hide")
        self.vim.command("setlocal noswapfile")

