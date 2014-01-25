#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Aparajita Fishman
# Copyright (c) 2013 Aparajita Fishman
#
# License: MIT
#

"""This module exports the PEP8 plugin linter class."""

import os

from SublimeLinter.lint import persist, PythonLinter


class PEP8(PythonLinter):

    """Provides an interface to the pep8 python module/script."""

    syntax = 'python'
    cmd = ('pep8@python', '*', '-')
    version_args = '--version'
    version_re = r'(?P<version>\d+\.\d+\.\d+)'
    version_requirement = '>= 1.4.6'
    regex = r'^.+?:(?P<line>\d+):(?P<col>\d+): (?:(?P<error>E)|(?P<warning>W))\d+ (?P<message>.+)'
    multiline = True
    defaults = {
        '--select=,': '',
        '--ignore=,': '',
        '--max-line-length=': None
    }
    inline_settings = 'max-line-length'
    inline_overrides = ('select', 'ignore')
    module = 'pep8'
    check_version = True

    # Internal
    report = None

    def check(self, code, filename):
        """Run pep8 on code and return the output."""

        options = {
            'reporter': self.get_report()
        }

        type_map = {
            'select': [],
            'ignore': [],
            'max-line-length': 0,
            'max-complexity': 0
        }

        self.build_options(options, type_map, transform=lambda s: s.replace('-', '_'))

        if persist.debug_mode():
            persist.printf('{} options: {}'.format(self.name, options))

        checker = self.module.StyleGuide(**options)

        return checker.input_file(
            filename=os.path.basename(filename),
            lines=code.splitlines(keepends=True)
        )

    def get_report(self):
        """Return the Report class for use by flake8."""
        if self.report is None:
            from pep8 import StandardReport

            class Report(StandardReport):

                """Provides a report in the form of a single multiline string, without printing."""

                def get_file_results(self):
                    """Collect and return the results for this file."""
                    self._deferred_print.sort()
                    results = ''

                    for line_number, offset, code, text, doc in self._deferred_print:
                        results += '{path}:{row}:{col}: {code} {text}\n'.format_map({
                            'path': self.filename,
                            'row': self.line_offset + line_number,
                            'col': offset + 1,
                            'code': code,
                            'text': text
                        })

                    return results

            self.__class__.report = Report

        return self.report
