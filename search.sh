#!/bin/bash
# Alfred Script Filter 入口：将工作目录设为脚本所在目录后调用 Python。
cd "$(dirname "$0")" || exit 1
exec /usr/bin/python3 ./search.py "$@"
