#!/usr/bin/env bash
set -o errexit -o pipefail -o nounset

readonly WORKING_DIRECTORY=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
readonly VENV_BIN_DIRECTORY="${WORKING_DIRECTORY}/.venv/bin"
readonly SOURCE_DIRECTORY="${WORKING_DIRECTORY}/src"
readonly TESTS_DIRECTORY="${WORKING_DIRECTORY}/src"

main() {
    ${VENV_BIN_DIRECTORY}/black --line-length=130 "${SOURCE_DIRECTORY}"
    ${VENV_BIN_DIRECTORY}/black --line-length=130 "${TESTS_DIRECTORY}"

    ${VENV_BIN_DIRECTORY}/mypy --ignore-missing-imports \
                                --cache-dir="${SOURCE_DIRECTORY}/.mypy_cache" \
                                "${SOURCE_DIRECTORY}"
}

main "$@"
