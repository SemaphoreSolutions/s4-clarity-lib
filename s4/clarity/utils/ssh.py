# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

import subprocess
import atexit
import logging
# Import appears unused, but replaces byte literals
from six import b


def tunnel(host, port, user):

    cmdline = ["ssh", "-o", "BatchMode=yes", "-vTNL",
               str(port) + ":localhost:" + str(port),
               user + "@" + host]
    logging.info("Establishing SSH tunnel to %s", host)
    logging.debug("Running: ", ' '.join(cmdline))
    tunnel_process = subprocess.Popen(cmdline, stderr=subprocess.PIPE)

    tunnel_ok = False
    nextline = b""
    stderr_buffer = []

    while True:
        c = tunnel_process.stderr.read(1)
        if c != b"\n":
            nextline += c
            continue
        line = nextline
        logging.debug(line)
        stderr_buffer.append(line)
        nextline = b""
        if b"forwarded to remote address" in line:
            tunnel_ok = True
        if b"debug1: Entering interactive session." in line:
            break

    def terminate_tunnel_at_exit():
        logging.info("SSH tunnel to %s terminated.", host)
        tunnel_process.terminate()

    atexit.register(terminate_tunnel_at_exit)

    tunnel_process.stderr.close()

    if not tunnel_ok:
        logging.error("Couldn't establish SSH tunnel.")
        for line in stderr_buffer:
            logging.error(line)
        exit(1)
