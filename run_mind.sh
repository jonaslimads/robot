#!/usr/bin/env bash
set -o errexit -o pipefail -o nounset

readonly WORKING_DIRECTORY=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
readonly BUILD_DIRECTORY="${WORKING_DIRECTORY}/build"

readonly MIND_DIRECTORY="${WORKING_DIRECTORY}/mind"
readonly MIND_VENV_DIRECTORY="${MIND_DIRECTORY}/.venv"
readonly MIND_VENV_BIN_DIRECTORY="${MIND_VENV_DIRECTORY}/bin"
readonly MIND_PYTHON="${MIND_VENV_BIN_DIRECTORY}/python"


# You may need to install:
# sudo apt-get install portaudio19-dev
# sudo apt-get install espeak

install() {

  if [[ -d "${MIND_VENV_DIRECTORY}" ]]; then
    return
  fi

  echo -e "No installation found. Installing mind..."

  cd "${MIND_DIRECTORY}"
  python3 -m venv .venv
  echo -e "Created virtualenv with $(${MIND_PYTHON} --version)"

  "${MIND_VENV_BIN_DIRECTORY}/pip" install -r requirements.txt
  echo -e "Packages installation done!"

  echo -e "Building remaining containers..."
  cd "${BUILD_DIRECTORY}"
  docker-compose build
}

run() {
  cd "${BUILD_DIRECTORY}"
  echo -e "Running containers in background..."
  docker-compose up -d

  "${MIND_PYTHON}" "${MIND_DIRECTORY}/app.py"
}  

main() {
  install
  run
}

main "$@"
