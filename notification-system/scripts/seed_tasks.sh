#!/usr/bin/env bash
# seed sample tasks
set -euo pipefail

API="${1:-http://localhost:8000}"
COUNT="${2:-10}"

echo "Seeding $COUNT tasks to $API"

for i in $(seq 1 $COUNT); do
  curl -s -X POST "$API/tasks" \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Sample Task $i\", \"payload\": \"seed payload $i\"}" | python3 -m json.tool
done
echo "seeded $COUNT tasks"
