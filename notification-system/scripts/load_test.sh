#!/usr/bin/env bash
# load test
set -euo pipefail

API="${1:-http://localhost:8000}"
REQUESTS="${2:-100}"
CONCURRENT="${3:-10}"

echo "Load test: $REQUESTS requests, $CONCURRENT concurrent"

for i in $(seq 1 $REQUESTS); do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST "$API/tasks" \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"load-test-$i\", \"payload\": \"batch $i\"}" &
  if (( i % CONCURRENT == 0 )); then
    wait
    echo "completed $i/$REQUESTS"
  fi
done
wait
echo "done"
