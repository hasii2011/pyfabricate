"""

"""
from setuptools import find_packages

from pyfabricate import __version__

from setuptools import setup

APP = ['pyfabricate/PyFabricateApp.py']

DATA_FILES = [('pyfabricate/resources', ['pyfabricate/resources/loggingConfiguration.json']),]
#               ('pygitissue2todoist/resources', ['pygitissue2todoist/resources/play.png']),
#               ('pygitissue2todoist/resources', ['pygitissue2todoist/resources/version.txt']),
#               ('pygitissue2todoist/resources', ['pygitissue2todoist/resources/packageversions.txt']),
#               ('pygitissue2todoist/resources', ['pygitissue2todoist/resources/SimpleHelp.html'])
#               ]

OPTIONS = {}

setup(
    name='PyFabricate',
    version=__version__,
    app=APP,
    packages=find_packages(include=['pyfabricate.*', 'mage.*']),
    include_package_data=True,
    data_files = DATA_FILES,
    zip_safe=False,
    url='https://github.com/hasii2011/pyfabricate',
    author='Humberto A. Sanchez II',
    author_email='Humberto.A.Sanchez.II@gmail.com',
    maintainer_email='humberto.a.sanchez.ii@gmail.com',
    description='Create an opinionated Python Project',
    options=dict(py2app=dict(
                    plist=dict(
                        CFBundleIdentifier='PyFabricate',
                        CFBundleShortVersionString=__version__,
                        LSEnvironment=dict(
                            APP_MODE='True',
                            PYTHONOPTIMIZE='1'
                        ),
                        LSMultipleInstancesProhibited='True',
                    ),
            ),
    ),
    setup_requires=['py2app'],
    install_requires=['codeallybasic>=1.4.0', 'wxPython>=4.2.2', 'semantic-version>=2.10.0']
)
