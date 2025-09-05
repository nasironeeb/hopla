#!/bin/bash

timestamp() {
  date +"%T" # current time
}

echo "Executing: $@"
echo "Start: $(timestamp)"
$@
echo "End: $(timestamp)"
echo "HOPLASAY-DONE"

