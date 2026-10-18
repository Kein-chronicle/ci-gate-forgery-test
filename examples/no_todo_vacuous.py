#!/usr/bin/env python3
"""A BLIND gate on purpose: 0 files measured -> exit 0 (green). The harness must catch this."""
import os, sys
files = [os.path.join(d, f) for d, _, fs in os.walk(sys.argv[1]) for f in fs]
sys.exit(1 if any("TODO" in open(f, errors="ignore").read() for f in files) else 0)
