#!/bin/bash

DOCKER_IMAGE_NAME=${1:-'python:2'}

# from: http://stackoverflow.com/q/59895/1784380
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  TARGET="$(readlink "$SOURCE")"
  if [[ $TARGET == /* ]]; then
    SOURCE="$TARGET"
  else
    DIR="$( dirname "$SOURCE" )"
    SOURCE="$DIR/$TARGET"
  fi
done

SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
STEINLIB_ROOT="$( dirname ${SCRIPT_DIR} )"

echo "Using steinlib from ${STEINLIB_ROOT}"
echo "Run a docker container ${DOCKER_IMAGE_NAME}"
docker run                         \
  --rm                             \
  -v ${STEINLIB_ROOT}:/work        \
  ${DOCKER_IMAGE_NAME}             \
  bash /work/scripts/run_tests.sh

echo "End."
