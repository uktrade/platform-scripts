#!/usr/bin/env bash

check_env_variables () {
    local missing_variables=()
    local env_var

    for env_var in "$@"; do
        [[ -n "${!env_var:-}" ]] || missing_variables+=("$env_var")
    done

    if [[ ${#missing_variables[@]} -gt 0 ]]; then
        echo "The following variables must be set in .env:"
        printf ' - %s\n' "${missing_variables[@]}"
        return 1
    fi
}