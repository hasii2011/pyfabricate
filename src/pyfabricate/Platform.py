
THE_GREAT_MAC_PLATFORM: str = 'macOS'

PYENV_CMD:             str = 'pyenv'

MAC_OS_PYENV_PATH:     str = f'/opt/homebrew/bin'
NON_MAC_OS_PYENV_PATH: str = f'/home/circleci/.pyenv/bin'

MAC_OS_PYENV_CMD:     str = f'{MAC_OS_PYENV_PATH}/{PYENV_CMD} versions'
NON_MAC_OS_PYENV_CMD: str = f'{NON_MAC_OS_PYENV_PATH}/{PYENV_CMD} versions'
