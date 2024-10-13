from typing import List
from unittest import TestSuite
from unittest import main as unitTestMain

from platform import platform as osPlatform

from codeallybasic.UnitTestBase import UnitTestBase

from pyfabricate.Platform import MAC_OS_PYENV_CMD
from pyfabricate.Platform import NON_MAC_OS_PYENV_CMD
from pyfabricate.Platform import THE_GREAT_MAC_PLATFORM
from pyfabricate.oswrapper.CompletedData import CompletedData
from pyfabricate.oswrapper.ExternalCommands import ExternalCommands
from pyfabricate.oswrapper.ExternalCommands import SemanticVersions
from pyfabricate.oswrapper.ExternalCommands import UnableToRetrievePythonVersionsException


# noinspection SpellCheckingInspection
TEST_STR: str = """
  system
  3.9.16
  3.10.10
  3.10.13
  3.11.0
  3.11.5
  3.11.7
  3.11.9
  3.12.0
  3.12.1
* 3.12.4 (set by /Users/humberto.a.sanchez.ii/PycharmProjects/pyfabricate/.python-version)
"""

TEST_LIST_LENGTH: int = 11      # The number of strings in TEST_STR


class TestExternalCommands(UnitTestBase):
    """
    Auto generated by the one and only:
        Gato Malo – Humberto A. Sanchez II
        Generated: 05 October 2024
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def testGetPythonVersions(self):

        try:
            pythonVersions: SemanticVersions = ExternalCommands.getPythonVersions()

            self.assertTrue(len(pythonVersions) > 0, 'Must find at least one installed version')
        except UnableToRetrievePythonVersionsException as e:
            self.logger.error(f'{e.stderr}')

    def testRunCommandFail(self):
        status: int = ExternalCommands.runCommand('/bogus/bin/fail')
        self.assertNotEqual(0, status, 'This should fail')

    def testRunCommandPass(self):
        platform: str = osPlatform(terse=True)
        print(f'{platform=}')
        if platform.startswith(THE_GREAT_MAC_PLATFORM) is True:
            status: int = ExternalCommands.runCommand(MAC_OS_PYENV_CMD)
        else:
            status = ExternalCommands.runCommand(NON_MAC_OS_PYENV_CMD)

        self.assertEqual(0, status, 'This should pass')

    def testRunCommandReturnOutput(self):

        platform: str = osPlatform(terse=True)
        if platform.startswith(THE_GREAT_MAC_PLATFORM) is True:
            completedData: CompletedData = ExternalCommands.runCommandReturnOutput(MAC_OS_PYENV_CMD)
        else:
            completedData = ExternalCommands.runCommandReturnOutput(NON_MAC_OS_PYENV_CMD)

        self.assertEqual(0, completedData.status)

    def testToList(self):

        retList: List[str] = ExternalCommands.toList(TEST_STR)

        self.assertEqual(TEST_LIST_LENGTH, len(retList))


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()

    testSuite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestExternalCommands))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
