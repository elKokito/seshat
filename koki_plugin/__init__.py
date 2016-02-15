#!/use/bin/env python3

import neovim
import os
import subprocess

from koki_plugin.koki_plugin import Koki


@neovim.plugin
class KokiFacade(object):

    def __init__(self, vim):
        # TODO .data/myinfo.json as to be initialized in case is empty
        self.vim = vim
        self.koki = Koki(vim)

    @neovim.function("MyFunc", sync=True)
    def MyFunc(self, *args, **kargs):
        return self.koki.project_command_completion()


    @neovim.command("Project", complete='customlist,MyFunc', range="", nargs="1", sync=False)
    def ProjectCommand(self, args, range):
        self.koki.project_command(args[0])


    @neovim.command("Diff", range="", nargs="*", sync=True)
    def DiffCommand(self, args, range):
        # get current HEAD and remote HEAD
        self.koki.diff_command()

    @neovim.command("LogStat", range="", nargs="*", sync=True)
    def LogStatCommand(self, args, range):
        self.koki.log_command()
