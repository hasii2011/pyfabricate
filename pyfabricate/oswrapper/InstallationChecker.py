

from logging import Logger
from logging import getLogger

class InstallationChecker:
    """
    Runs a version of a command line interface (CLI) to ensure
    that it executes.  If the command returns a zero status, we assume
    it is correctly installed.

    Examples are:

        pyenv --version
        jq    --version
        curl  --version

    Most of the methods here are `class methods`, so you do not have to actually
    instantiate a version of this class

    TODO:  Move this to the codeallybasic module.  Remove the duplicated code in the
    latestversions Python script CLI
    """
    def __init__(self):
        self.logger: Logger = getLogger(__name__)
