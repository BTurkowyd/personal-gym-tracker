#!/bin/bash

# Get the current Git branch name
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# Print the branch name as JSON
echo "{ \"branch\": \"$BRANCH_NAME\" }"
