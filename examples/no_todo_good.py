#!/usr/bin/env python3
"""A correct gate: fails on TODO, and fails when it measured nothing."""
import os, sys
root = sys.argv[1]
if not os.path.isdir(root): sys.exit(2)
files = [os.path.join(d, f) for d, _, fs in os.walk(root) for f in fs]
if not files: print("measured 0 files - not a pass"); sys.exit(3)
hits = [f for f in files if "TODO" in open(f, errors="ignore").read()]
sys.exit(1 if hits else 0)
