import json
import os
from string import ascii_lowercase

from koki_plugin.utils.git_utils import git_diff, git_log, is_inside_repo,\
                                        git_get_root_path

PLUGIN_METADATA_PATH = os.path.dirname(__file__) + "/.data"
METADATA_FILE = "/metainfo.json"


class Koki(object):

    def __init__(self, vim):
        self._validate_initial_data()
        self.vim = vim

    def project_command(self, project_name):
        project_path = self.vim.command_output("echo expand('%:p:h')").split("\n")[1]
        project_name = project_name
        projects = self._read_json(METADATA_FILE)
        if project_name in projects["projects"]:
            # open project as it was
            # with tabs
            project = projects[project_name]
            for tab in project["tabs"]:
                self.vim.command("tabnew " + tab)
            self.vim.command("tabclose 1")
        else:
            # check if its a git repo
            projects[project_name] = {"project_path": project_path, "tags_file_path": "", "tabs": []}
            projects["projects"].append(project_name)
            if is_inside_repo():
                project_git_root_path = git_get_root_path()
                projects[project_name].update({"git_root_path": project_git_root_path})
            self._write_to_json(projects, METADATA_FILE)

    def project_command_completion(self):
        projects = self._read_json(METADATA_FILE)
        return projects["projects"]

    def save_command(self):
        # get tabs on current session
        tabs = []
        for tab in self.vim.tabpages:
            tabs.append(tab.window.buffer.name)

        # get current session got from current path
        project_name = self._get_project_from_path(str(self.vim.current.buffer.name))
        if project_name is None:
            # display error message
            self.vim.command("echo 'Not in a project directory'")
        else:
            projects = self._read_json(METADATA_FILE)
            projects[project_name].update({"tabs": tabs})
            self._write_to_json(projects, METADATA_FILE)

    def bookmark_command(self, bookmark_name):
        bookmark_path = self.vim.current.buffer.name
        metadata = self._read_json(METADATA_FILE)
        for bookmark in metadata["bookmarks"]:
            if bookmark_name == bookmark["bookmark_name"]:
                self.vim.command("e " + bookmark["bookmark_path"])
                return
        # add bookmark
        new_bookmark = {"bookmark_name": bookmark_name, "bookmark_path": bookmark_path}
        metadata["bookmarks"].append(new_bookmark)
        self._write_to_json(metadata, METADATA_FILE)

    def bookmark_command_completion(self):
        metadata = self._read_json(METADATA_FILE)
        bookmark_name_list = [bookmark["bookmark_name"] for bookmark in metadata["bookmarks"]]
        return bookmark_name_list

    def VimEnter_autocmd(self):
        # rename buffer
        self.vim.command("file seshat")
        metadata = self._read_json(METADATA_FILE)
        # set buffer as scractch
        self.vim.command("setlocal buftype=nofile")
        self.vim.command("setlocal bufhidden=hide")
        self.vim.command("setlocal noswapfile")
        self.vim.command("setlocal nonumber")
        # clean command line
        self.vim.command("echo ''")

        # write project per line
        width = self.vim.current.window.width
        height = self.vim.current.window.height
        space = int(width/4)

        projects = metadata["projects"]
        bookmarks = [b["bookmark_name"] for b in metadata["bookmarks"]]

        projects_lines = []
        # project list
        for i in range(len(projects)):
            line = " " * space + "[" + str(i) + "] : " + projects[i]
            self.vim.command("nnoremap <buffer> " + str(i) + " :Project " + projects[i] + "<CR>")
            projects_lines.append(line)

        bookmarks_lines = []
        # bookmark list
        for i in range(len(bookmarks)):
            line = "[" + ascii_lowercase[i] + "] : " + bookmarks[i]
            self.vim.command("nnoremap <buffer> " + ascii_lowercase[i] + " :Bookmark " + bookmarks[i] + "<CR>")
            bookmarks_lines.append(line)

        buffer = []
        for i in range(int(height/2)):
            buffer.append("")
        for i in range(len(min(bookmarks_lines, projects_lines))):
            space = int(width/2)-len(projects_lines[i])
            line = projects_lines[i] + " " * space + bookmarks_lines[i]
            buffer.append(line)

        if bookmarks_lines == max(bookmarks_lines, projects_lines):
            for i in range(len(min(bookmarks_lines, projects_lines)), len(bookmarks_lines)):
                line = " " * int(width/2) + bookmarks_lines[i]
                buffer.append(line)

        self.vim.current.buffer[:] = buffer

    def diff_command(self):
        diff_list = git_diff()
        self._new_scratch_buffer("git diff")
        self.vim.current.buffer[:] = diff_list

    def log_command(self):
        self._new_scratch_buffer("git log")
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

    def _new_scratch_buffer(self, name):
        self.vim.command("tabnew " + name)
        self.vim.command("setlocal buftype=nofile")
        self.vim.command("setlocal bufhidden=hide")
        self.vim.command("setlocal noswapfile")

    def _validate_initial_data(self):
        if not os.path.isfile(PLUGIN_METADATA_PATH + METADATA_FILE):
            initial_metadata = {"projects": [], "bookmarks": []}
            with open(PLUGIN_METADATA_PATH + METADATA_FILE, "w") as fd:
                json.dump(initial_metadata, fd, indent=4)

    def _get_project_from_path(self, path):
        projects = self._read_json(METADATA_FILE)
        for project_name in projects["projects"]:
            if path.find(projects[project_name]["project_path"]) != -1:
                return project_name
        return None
