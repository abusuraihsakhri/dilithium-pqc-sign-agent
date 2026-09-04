#!/usr/bin/env python3
import os
import sys

# Ensure audit key is set before importing modules that use it
os.environ.setdefault("AUDIT_SECRET_KEY", "cli-audit-key-for-local-use-only-2026")

from dilithium_sign.cli import main

if __name__ == '__main__':
    sys.exit(main())
