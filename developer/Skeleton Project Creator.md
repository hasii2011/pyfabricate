# Skeleton Project Creator

The following is a directory graphic of a typical Python project which I manually create.  The purpose of this Python script is to automate the process of creating a Python project.

![SampleDocumentStructure](.//SampleDocumentStructure.png)

## Opionated Assumptions

- The developer uses [HomeBrew](https://brew.sh) to install the opinionated dependencies.
    - Python is managed via pyenv (For use in the created virtual environments)
    - direnv is installed
    - The developer installed a [HomeBrew](https://brew.sh) version of Python (For creating the virtual environments)

- The project name is the same as the module package name

## Steps

1. Ask project name (`PROJECT_NAME`)

2. Ask the following information for pyproject.toml
    1. name (to appear in pyproject.toml)
    2. Owner name
    3. Ask email (to app)
    4. Project description
    5. Project keywords

3. Ask python version (list them - `pyenv versions`)

4. Ask for the base directory for the developers python projects e.g. `PROJECTS_BASE=/Users/humberto.a.sanchez.ii/PycharmProjects`

5. Create the project directory
    ${PROJECTS_BASE}/{ProjectName}                               

6. Create the local virtual environment `python -m venv pyenv-<PYTHON_VERSION>`

7. Create the following files using our templates
    1.  .envrc  (Remind developer to execute direnv allow)
    2.  .mypy.ini
    3.  .gitignore
    4.  README 
    5.  requirements.txt
    6.  pyproject.toml
    7.  .circleci/config.yml
    8.  src/_version.py
    9.  src/PROJECT_NAME/resources/loggingConfiguration.json
    10.  tests/PROJECT_NAME/resources/testLoggingConfiguration.json

8. Set the requested version as local version `pyenv local <request version>`

    

## Update _version.py 

```python
__version__: str = '0.1.0'
```

Update __init__.py

```python
from PROJECT_NAME._version import __version__

```


## Templates

### .envrc
```bash
export PROJECT=<PPROJECT_NAME>
source pyenv-<PYTHON_VERSION>/bin/activate
```
### .mypy.ini
```ini
[mypy]
python_version = 3.12
pretty = True
warn_unused_ignores = True
implicit_optional = True
strict_equality = True

[mypy-HtmlTestRunner.*]
ignore_missing_imports = True
```
### .gitignore
```
#Ignored files
.idea/
__pycache__/
.DS_Store
build/
dist/
/src/<PROJECT_NAME>.egg-info/
/pyenv-<PYTHON VERSION>/
.python-version
.envrc
```
### requirements.txt
```
wheel==0.43.0
setuptools==69.2.0
twine==5.0.0
build == 1.2.2
mypy == 1.11.2
html-testRunner~=1.2.1
click == 8.1.7
codeallybasic == 1.4.0
# So Circle CI works
buildlackey==1.6.3
```

### pyproject.toml

```toml
[build-system]
requires = ['setuptools', 'wheel']
build-backend = "setuptools.build_meta"

[project]
name=<PROJECT_NAME>
dynamic = ["version"]
description = DEVELOPER PROVIDED DESCRIPTION
readme = "README.md"
license = {text = 'GNU AFFERO GENERAL PUBLIC LICENSE'}
authors = [{name = DEVELOPER PROVIDED NAME, email = DEVELOPER PROVIDED EMAIL]
maintainers = [{name = DEVELOPER PROVIDED NAME, email = DEVELOPER PROVIDED EMAIL}]
keywords = [DEVELOPER PROVIDED KEY WORDS]

dependencies = [

]

[project.urls]
Repository = 'https://github.com/GITHUBUSER NAME/$PROJECT_NAME'

[tool.setuptools.packages.find]
where = ['src']

[tool.setuptools.package-data]
'$PROJECT_NAME.resources' = ['loggingConfiguration.json']

[tool.setuptools.dynamic]
version = {attr = '$PROJECT_NAME.__version__'}

```

### config.yml



```yaml
version: '2.1'

orbs:
  python: circleci/python@2.1.1

workflows:
  main:
    jobs:
      - build:
          filters:
            tags:
              only: /.*/

jobs:
  build:
    docker:
      - image: cimg/python:3.10
    executor: python/default
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
      - run:
            name: run tests
            command: | 
              unittests
```

### loggingConfiguration.json

```json
{
    "version": 1,
    "disable_existing_loggers": "False",
    "formatters": {
        "simple": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s"
        },
        "testSimple": {
            "format": "%(levelname)s: %(module)s: %(message)s"
        }
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "formatter": "testSimple",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "root": {
            "level": "WARNING",
            "handlers": ["consoleHandler"],
            "propagate": "False"
        },
        "__main__": {
            "level": "INFO",
            "propagate": "False"
        },
        "$PROJECT_NAME": {
            "level": "INFO",
            "propagate": "False"
        }
    }
}
```



testLoggingConfiguration.json

```json
{
    "version": 1,
    "disable_existing_loggers": "False",
    "formatters": {
        "simple": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)s %(module)s: %(message)s"
        },
        "testSimple": {
            "format": "%(levelname)s: %(module)s: %(message)s"
        }
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "formatter": "testSimple",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "root": {
            "level": "WARNING",
            "handlers": ["consoleHandler"],
            "propagate": "False"
        },
        "__main__": {
            "level": "INFO",
            "propagate": "False"
        },
        "codeallybasic.UnitTestBase": {
            "level":     "INFO",
            "propagate": "False"
        }
    }
}
```

