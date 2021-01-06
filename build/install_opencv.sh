#!/usr/bin/env bash
set -o errexit -o pipefail -o nounset

readonly WORKING_DIRECTORY=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
readonly VENV_BIN_DIRECTORY="${WORKING_DIRECTORY}/venv/bin"

main() {
  if [[ -d "${WORKING_DIRECTORY}/venv" ]]; then
    echo "venv folder exists with $(${VENV_BIN_DIRECTORY}/python --version) and following packages:"
    "${VENV_BIN_DIRECTORY}/pip" freeze
    exit 1
  fi

  cd "${WORKING_DIRECTORY}"
  python3 -m venv venv
  echo -e "Created virtualenv with $(${VENV_BIN_DIRECTORY}/python --version)"

  "${VENV_BIN_DIRECTORY}/pip" install -r requirements.txt
  echo "Packages installation done! You can now run the examples."
}

main "$@"

