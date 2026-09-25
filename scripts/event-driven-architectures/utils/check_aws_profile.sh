#!/usr/bin/env bash

# TODO: update to handle multiple profiles
check_aws_profile () {
    if [[ "$AWS_PROFILE" != "platform-sandbox" ]]; then
        echo "The currently selected AWS_PROFILE ('$AWS_PROFILE') is not permitted; set AWS_PROFILE to 'platform-sandbox' to run this script"
        return 1
    fi
}