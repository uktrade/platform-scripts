#!/usr/bin/env bash
export AWS_PAGER=""

if [[ ! -f .env ]]; then
    echo ".env file not found, exiting script"
    exit 1
fi

source .env

source utils/check_aws_profile.sh
check_aws_profile || exit 1

source utils/check_env_variables.sh
check_env_variables "SNS_TOPIC" "TOTAL_NUMBER_OF_MESSAGES" || exit 1

mapfile -t messages < <(
    for ((i=1; i<=TOTAL_NUMBER_OF_MESSAGES; i++)); do
        echo "Message number: $i"
    done
)

publish_message () {
    local sns_topic=$1
    local message=$2
    aws sns publish --topic-arn "$sns_topic" --message "$message"
}

echo "Publishing messages"
for message in "${messages[@]}"; do
    publish_message "$SNS_TOPIC" "$message"
done
