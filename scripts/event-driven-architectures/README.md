# Scripts for testing event-driven architecture (SNS+SQS)

## Purpose
- Generating and publishing messages to a specified SNS topic, see `publish_messages.sh`.
- Consuming messages that a subscribing SQS queue receives from an SNS topic, see `process_messages.sh`. 

## How to use
Within the `./scripts/event-driven-architectures` directory, define an `.env` file with the required environment variables. You can find out what variables are required by looking at the `check_env_variables` function calls within the scripts. For example, `check_env_variables "SNS_TOPIC" "TOTAL_NUMBER_OF_MESSAGES"` would require an `.env` file with the following (dummy values):

```
SNS_TOPIC="<sns-topic-arn>"
TOTAL_NUMBER_OF_MESSAGES="<number-of-messages-to-publish>"
```

Login to AWS with:

```
aws sso login
```

Export the AWS profile of the account you want to run this script in (currently only `platform-sandbox` is supported):

```
export AWS_PROFILE=platform-sandbox
```

Run the selected script from within the `./scripts/event-driven-architectures` directory, e.g `publish_messages.sh`

```
bash publish_messages.sh
```

## Notes
Remember to delete messages from the SQS queue once finished. This can be done with `process_messages.sh`.