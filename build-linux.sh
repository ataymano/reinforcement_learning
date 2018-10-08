#!/bin/bash

set -e

# Build vw dependency
cd ext_libs/vowpal_wabbit/vowpalwabbit
make vw
cd ../../..

# Build reinforcement_learning
mkdir -p build
cd build
cmake ..
make -j
make test