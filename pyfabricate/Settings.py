
from pathlib import Path

from codeallybasic.DynamicConfiguration import DynamicConfiguration
from codeallybasic.DynamicConfiguration import KeyName
from codeallybasic.DynamicConfiguration import SectionName
from codeallybasic.DynamicConfiguration import Sections
from codeallybasic.DynamicConfiguration import ValueDescription
from codeallybasic.DynamicConfiguration import ValueDescriptions

from codeallybasic.SingletonV3 import SingletonV3

from pyfabricate.Constants import APPLICATION_NAME


def toPath(pathString: str) -> Path:
    return Path(pathString)


PROJECT_PROPERTIES: ValueDescriptions = ValueDescriptions(
    {
        KeyName('name'):          ValueDescription(defaultValue='projectName'),
        KeyName('ownerName'):     ValueDescription(defaultValue='Humberto A. Sanchez II'),
        KeyName('ownerEmail'):    ValueDescription(defaultValue='Humberto.A.Sanchez.II@gmail.com'),
        KeyName('description'):   ValueDescription(defaultValue='This is a good project'),
        KeyName('keywords'):      ValueDescription(defaultValue='keyword1,keyword2,keyword3'),
        KeyName('baseDirectory'): ValueDescription(defaultValue=f'{Path.home()}', deserializer=toPath),
    }
)

SETTINGS_SECTIONS: Sections = Sections(
    {
        SectionName('Project'): PROJECT_PROPERTIES,
    }
)


class Settings(DynamicConfiguration, metaclass=SingletonV3):
    def __init__(self):

        super().__init__(baseFileName=f'{APPLICATION_NAME}.ini', moduleName=APPLICATION_NAME, sections=SETTINGS_SECTIONS)

