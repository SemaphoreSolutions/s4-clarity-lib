# Copyright 2019 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
import re


def standard_sort_key(s):
    cells = [c for c in re.split(r'(\d+)?(\D+)', s) if c]
    for i, cell in enumerate(cells):
        if cell.isdigit():
            # format cell length to be zero padded to 2 digits
            cells[i] = '%02d%s' % (len(cell), cell)
    return ''.join(cells)
