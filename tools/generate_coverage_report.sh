#!/usr/bin/env bash
# SPDX-License-Identifier: LGPL-2.1-or-later

# This script runs lcov to extract and generate code coverage reports for C++
# code. It is designed for GNU/GCC and Clang compiler builds on Linux/macOS.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/debug"
OUTPUT_DIR="${ROOT_DIR}/coverage_report"

echo "========================================="
echo "Generating C++ Code Coverage Report"
echo "========================================="

# Check if lcov is installed
if ! command -v lcov &> /dev/null; then
    echo "Error: lcov is not installed. Please install it first (e.g. 'sudo apt install lcov')."
    exit 1
fi

# Check if genhtml is installed
if ! command -v genhtml &> /dev/null; then
    echo "Error: genhtml is not installed. Please install it first (e.g. 'sudo apt install lcov')."
    exit 1
fi

# Ensure build directory exists
if [ ! -d "${BUILD_DIR}" ]; then
    echo "Error: Build directory '${BUILD_DIR}' not found. Please build FreeCAD with coverage enabled first."
    exit 1
fi

# Step 1: Capture coverage data
echo "Step 1: Capturing coverage data from ${BUILD_DIR}..."
lcov --capture --directory "${BUILD_DIR}" --output-file "${BUILD_DIR}/coverage.info"

# Step 2: Filter out third-party libraries and test files
echo "Step 2: Filtering out external and test files..."
lcov --remove "${BUILD_DIR}/coverage.info" \
    '/usr/*' \
    '*/tests/*' \
    '*/3rdParty/*' \
    '*/boost/*' \
    '*/eigen/*' \
    '*/qt/*' \
    --output-file "${BUILD_DIR}/coverage.filtered.info"

# Step 3: Generate HTML report
echo "Step 3: Generating HTML report in ${OUTPUT_DIR}..."
rm -rf "${OUTPUT_DIR}"
genhtml "${BUILD_DIR}/coverage.filtered.info" --output-directory "${OUTPUT_DIR}"

echo "========================================="
echo "Coverage report generated successfully!"
echo "Open ${OUTPUT_DIR}/index.html in your browser."
echo "========================================="
