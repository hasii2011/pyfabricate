
from typing import cast

from logging import Logger
from logging import getLogger

from pathlib import Path

from codeallybasic.ConfigurationProperties import ConfigurationNameValue
from codeallybasic.ConfigurationProperties import ConfigurationProperties
from codeallybasic.ConfigurationProperties import PropertyName
from codeallybasic.ConfigurationProperties import Section
from codeallybasic.ConfigurationProperties import SectionName
from codeallybasic.ConfigurationProperties import Sections
from codeallybasic.ConfigurationProperties import configurationGetter
from codeallybasic.ConfigurationProperties import configurationSetter

from codeallybasic.SingletonV3 import SingletonV3

from pyfabricate.Constants import APPLICATION_NAME

PROJECT_SECTION_NAME: SectionName = SectionName('Project')

SECTION_PROJECT: Section = Section(
    [
        ConfigurationNameValue(name=PropertyName('name'),          defaultValue=f'projectName'),
        ConfigurationNameValue(name=PropertyName('ownerName'),     defaultValue=f'Humberto A. Sanchez II'),
        ConfigurationNameValue(name=PropertyName('ownerEmail'),    defaultValue=f'Humberto.A.Sanchez.II@gmail.com'),
        ConfigurationNameValue(name=PropertyName('description'),   defaultValue=f'This is a good project'),
        ConfigurationNameValue(name=PropertyName('keywords'),      defaultValue=f'keyword1,keyword2'),
        ConfigurationNameValue(name=PropertyName('baseDirectory'), defaultValue=f'{Path.home()}'),
    ]
)

SETTINGS_SECTIONS: Sections = Sections(
    {
        PROJECT_SECTION_NAME: SECTION_PROJECT,
    }
)


def toPath(pathString: str) -> Path:
    return Path(pathString)


class Settings(ConfigurationProperties, metaclass=SingletonV3):
    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        super().__init__(baseFileName=f'{APPLICATION_NAME}.ini', moduleName=APPLICATION_NAME, sections=SETTINGS_SECTIONS)

        self._configParser.optionxform = self._toStr    # type: ignore
        self._loadConfiguration()

    @property
    @configurationGetter(sectionName=PROJECT_SECTION_NAME)
    def name(self) -> str:
        return ''

    @name.setter
    @configurationSetter(sectionName=PROJECT_SECTION_NAME)
    def name(self, newValue: str):
        pass

    @property
    @configurationGetter(sectionName=PROJECT_SECTION_NAME)
    def ownerName(self) -> str:
        return ''

    @ownerName.setter
    @configurationSetter(sectionName=PROJECT_SECTION_NAME)
    def ownerName(self, newValue: str):
        pass

    @property
    @configurationGetter(sectionName=PROJECT_SECTION_NAME)
    def ownerEmail(self) -> str:
        return ''

    @ownerEmail.setter
    @configurationSetter(sectionName=PROJECT_SECTION_NAME)
    def ownerEmail(self, newValue: str):
        pass

    @property
    @configurationGetter(sectionName=PROJECT_SECTION_NAME)
    def description(self) -> str:
        return ''

    @description.setter
    @configurationSetter(sectionName=PROJECT_SECTION_NAME)
    def description(self, newValue: str):
        pass

    @property
    @configurationGetter(sectionName=PROJECT_SECTION_NAME)
    def keywords(self) -> str:
        return ''

    @keywords.setter
    @configurationSetter(sectionName=PROJECT_SECTION_NAME)
    def keywords(self, newValue: str):
        pass

    @property
    @configurationGetter(sectionName=PROJECT_SECTION_NAME, deserializeFunction=toPath)
    def baseDirectory(self) -> Path:
        return cast(Path, None)     # never used

    @baseDirectory.setter
    @configurationSetter(sectionName=PROJECT_SECTION_NAME)
    def baseDirectory(self, newValue: Path):
        pass

    def _toStr(self, optionString: str) -> str:
        """
        Override base method

        Args:
            optionString:

        Returns: The option string unchanged
        """
        return optionString
