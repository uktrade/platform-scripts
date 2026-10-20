#!/usr/bin/env bash

check_aws_profile () {
    if [[ "$AWS_PROFILE" =~ "prod" ]]; then
        echo "The currently selected AWS_PROFILE ('$AWS_PROFILE') is not permitted; only non-prod profiles are allowed to be used in this script"
        return 1
    fi
}
