#!/usr/bin/env bash
set -o errexit -o pipefail -o nounset

readonly WORKING_DIRECTORY=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
readonly VENV_BIN_DIRECTORY="${WORKING_DIRECTORY}/build/venv/bin"
readonly PYTHON=${VENV_BIN_DIRECTORY}/python

main() {
  cd "${WORKING_DIRECTORY}/build"
  docker-compose up -d
  cd "${WORKING_DIRECTORY}"
  "${PYTHON}" ai/server/app
}

main "$@"
