#!/bin/sh
if echo "$1" | grep -q "ECHO is off"; then
  echo "fix: clean up temporary files and update system logs"
else
  cat
fi
