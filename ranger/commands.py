# This is a sample commands.py.  You can add your own commands here.
#
# Please refer to commands_full.py for all the default commands and a complete
# documentation.  Do NOT add them all here, or you may end up with defunct
# commands when upgrading ranger.

# A simple command for demonstration purposes follows.
# -----------------------------------------------------------------------------

from __future__ import (absolute_import, division, print_function)

# You can import any python module as needed.
import os

# You always need to import ranger.api.commands here to get the Command class:
from ranger.api.commands import Command


# Any class that is a subclass of "Command" will be integrated into ranger as a
# command.  Try typing ":my_edit<ENTER>" in ranger!
class my_edit(Command):
    # The so-called doc-string of the class will be visible in the built-in
    # help that is accessible by typing "?c" inside ranger.
    """:my_edit <filename>

    A sample command for demonstration purposes that opens a file in an editor.
    """

    # The execute method is called when you run this command in ranger.
    def execute(self):
        # self.arg(1) is the first (space-separated) argument to the function.
        # This way you can write ":my_edit somefilename<ENTER>".
        if self.arg(1):
            # self.rest(1) contains self.arg(1) and everything that follows
            target_filename = self.rest(1)
        else:
            # self.fm is a ranger.core.filemanager.FileManager object and gives
            # you access to internals of ranger.
            # self.fm.thisfile is a ranger.container.file.File object and is a
            # reference to the currently selected file.
            target_filename = self.fm.thisfile.path

        # This is a generic function to print text in ranger.
        self.fm.notify("Let's edit the file " + target_filename + "!")

        # Using bad=True in fm.notify allows you to print error messages:
        if not os.path.exists(target_filename):
            self.fm.notify("The given file does not exist!", bad=True)
            return

        # This executes a function from ranger.core.acitons, a module with a
        # variety of subroutines that can help you construct commands.
        # Check out the source, or run "pydoc ranger.core.actions" for a list.
        self.fm.edit_file(target_filename)

    # The tab method is called when you press tab, and should return a list of
    # suggestions that the user will tab through.
    # tabnum is 1 for <TAB> and -1 for <S-TAB> by default
    def tab(self, tabnum):
        # This is a generic tab-completion function that iterates through the
        # content of the current directory.
        return self._tab_directory_content()


class yank(Command):
    """:yank [name|dir|path]

    Copies the file's name (default), directory or path into both the primary X
    selection and the clipboard.
    """

    modes = {
        '': 'basename',
        'name_without_extension': 'basename_without_extension',
        'name': 'basename',
        'dir': 'dirname',
        'path': 'path',
    }

    def execute(self):
        import subprocess

        def clipboards():
            from ranger.ext.get_executables import get_executables
            clipboard_managers = {
                'xclip': [
                    ['xclip'],
                    ['xclip', '-selection', 'clipboard'],
                ],
                'xsel': [
                    ['xsel'],
                    ['xsel', '-b'],
                ],
                'wl-copy': [
                    ['wl-copy'],
                ],
                'pbcopy': [
                    ['pbcopy'],
                ],
            }
            ordered_managers = ['pbcopy', 'wl-copy', 'xclip']
            executables = get_executables()
            for manager in ordered_managers:
                if manager in executables:
                    return clipboard_managers[manager]
            return []

        clipboard_commands = clipboards()

        mode = self.modes[self.arg(1)]
        selection = self.get_selection_attr(mode)

        new_clipboard_contents = "\n".join(selection)
        for command in clipboard_commands:
            process = subprocess.Popen(command, universal_newlines=True,
                                       stdin=subprocess.PIPE)
            process.communicate(input=new_clipboard_contents)

    def get_selection_attr(self, attr):
        return [getattr(item, attr) for item in
                self.fm.thistab.get_selection()]

    def tab(self, tabnum):
        return (
            self.start(1) + mode for mode
            in sorted(self.modes.keys())
            if mode
        )
