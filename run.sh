#!/usr/bin/env bash
set -e

if [[ "$1" == "--build" ]]; then
  shift
  docker build --target app -t wikipedia-philosophy-app . -q
fi

docker run --rm -it wikipedia-philosophy-app "$@"
