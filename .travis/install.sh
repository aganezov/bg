#!/usr/bin/env bash

if [ "$TRAVIS_OS_NAME" = 'osx' ]; then
    brew update
    brew tap homebrew/science
    brew install pyenv
    brew install mercurial
    case "$PYTHON" in
    "2.7")
     pyenv install 2.7.11
     pyenv global 2.7.11
     ;;
     "3.4")
     pyenv install 3.4.3
     pyenv global 3.4.3
     ;;
     "3.5")
     pyenv install 3.5.1
     pyenv global 3.5.1
     ;;
    esac
    `pyenv which pip` install virtualenv
    `pyenv which virtualenv` bg-env
fi

if [ "$TRAVIS_OS_NAME" = 'linux' ]; then
    sudo apt-get update
    pip install virtualenv
    virtualenv bg-env
fi