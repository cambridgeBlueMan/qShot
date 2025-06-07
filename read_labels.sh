#!/bin/bash
# This script reads a file called labels.txt and creates directories for each label
# in the current directory. It also creates subdirectories for each type (train, test, val).
# Check if labels.txt exists
if [ ! -f labels.txt ]; then
    echo "labels.txt not found!"
    exit 1
fi
types=("train" "test" "val")
# Create directories for each type
for type in "${types[@]}"; do
    # Create a directory for each type
    mkdir -p $type
    cd $type
    # Read a file line by line
    while IFS= read -r line; do
        mkdir -p $line
    done < ../labels.txt
    cd ..
done
