#!/use/bin/env python3

import neovim

from koki_plugin.koki_plugin import Koki


@neovim.plugin
class KokiFacade(object):

    def __init__(self, vim):
        # TODO .data/myinfo.json as to be initialized in case is empty
        self.vim = vim
        self.koki = Koki(vim)

    """
    functions
    """
    @neovim.function("ProjectCommandCompletion", sync=True)
    def ProjectCommandCompletion(self, *args, **kargs):
        return self.koki.project_command_completion()

    @neovim.function("BookmarkCommandCompletion", sync=True)
    def BookmarkCommandCompletion(self, *args, **kargs):
        return self.koki.bookmark_command_completion()

    """
    projects commands
    """
    @neovim.command("Project", complete='customlist,ProjectCommandCompletion', range="", nargs="1", sync=False)
    def ProjectCommand(self, args, range):
        self.koki.project_command(args[0])

    @neovim.command("Save", range="", nargs="*", sync=False)
    def SaveCommand(self, args, range):
        self.koki.save_command()

    @neovim.command("Bookmark", complete="customlist,BookmarkCommandCompletion", range="", nargs="1", sync=False)
    def BookmarkCommand(self, args, range):
        self.koki.bookmark_command(args[0])

    """
    git commands
    """
    @neovim.command("Diff", range="", nargs="*", sync=True)
    def DiffCommand(self, args, range):
        # get current HEAD and remote HEAD
        self.koki.diff_command()

    @neovim.command("LogStat", range="", nargs="*", sync=True)
    def LogStatCommand(self, args, range):
        self.koki.log_command()

    """
    autocmds
    """
    @neovim.autocmd("VimEnter", pattern="*", sync=True)
    def VimEnterAutoCmd(self):
        # if entered vim with file to open
        args = self.vim.eval("expand('%')")
        if args == "":
            self.koki.VimEnter_autocmd()
        else:
            pass
