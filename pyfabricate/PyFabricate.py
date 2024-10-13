
from logging import Logger
from logging import getLogger

from click import ClickException
from click import command
from click import version_option

from pyfabricate import __version__
from pyfabricate.UnknownGitHubRepositoryException import UnknownGitHubRepositoryException


class PyFabricate:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    def startUI(self):
        pass


@command()
@version_option(version=f'{__version__}', message='%(version)s')
def commandHandler():
    """

    """
    try:
        gh2md: PyFabricate = PyFabricate()

        gh2md.startUI()

    except UnknownGitHubRepositoryException:
        raise ClickException(f'Unknown GitHub Repository')


if __name__ == "__main__":

    # commandHandler(['-s', 'hasii2011/code-ally-advanced', '-d', '2024-02-01', '-o', 'codeallyadvanced.md'])
    commandHandler(['--help'])
    # commandHandler(['-s', 'hasii2011/code-ally-advanced', '-d', '204-02-01', '-o', 'codeallyadvanced.md'])
