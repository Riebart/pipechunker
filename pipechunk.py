#!/usr/bin/env python3

import argparse
import json
import logging
import subprocess
import sys
import threading
import time

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel("DEBUG")


class JSONList(object):
    def __call__(self, *args, **kwargs):
        try:
            arg = json.loads(args[0])
            if not isinstance(arg, list):
                return [arg]
            else:
                return arg
        except:
            return [args[0]]


def handle_chunk(chunk_data, command, chunk_name, dry_run):
    if dry_run:
        logger.debug("Would have passed in %d bytes to \"%s\"" %
                     (len(chunk_data), str(command + [chunk_name])))
    else:
        logger.info("Creating process for chunk %s" % chunk_name)
        proc = subprocess.Popen(command + [chunk_name], stdin=subprocess.PIPE)
        proc.stdin.write(chunk_data)
        proc.stdin.close()
        logger.info("done")
        while proc.poll() is None:
            time.sleep(1)
        return proc.returncode


def main(parsed_args):
    chunk_size = parsed_args.chunk_size
    threads = []

    # For each chunk:
    # - Read in the chunk_size of bytes
    # - Spawn a process, and send the chunk data to the process
    # - Track the process
    #
    # For the set of processes:
    # - Check on each one every second.
    # - If there is a finished one, repeat the per-chunk workload.
    chunk_num = 1
    eof = False
    while not eof:
        while len(threads) < parsed_args.parallel and not eof:
            chunk_data = sys.stdin.buffer.read(chunk_size)
            eof = len(chunk_data) < chunk_size
            if len(chunk_data) > 0:
                logger.info("Creating thread %d" % chunk_num)
                thread = threading.Thread(
                    target=lambda cd=chunk_data,
                                  c=parsed_args.command,
                                  cn=parsed_args.name + ".%04d" % (chunk_num, ),
                                  dr=parsed_args.dry_run:
                                    handle_chunk(cd, c, cn, dr))
                logger.info("Starting thread %d" % chunk_num)
                thread.start()
                threads.append(thread)
                chunk_num += 1
        time.sleep(5)
        logger.info("Checking threads")
        threads = [t for t in threads if t.is_alive()]
        logger.info("Found %d live threads out of %d" % (len(threads),
                                                         parsed_args.parallel))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=
        "Chunk a data on stdin into chunks of a given size, and invoke an action on each chunk."
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        required=True,
        help="""Chunk size, in bytes""")
    parser.add_argument(
        "--command",
        type=JSONList(),
        required=True,
        help="""Path to binary to invoke""")
    parser.add_argument(
        "--name",
        required=True,
        help=
        """Prefix of chunk name, passed to command. Will have ".$chunkNumber" appended to it."""
    )
    parser.add_argument(
        "--parallel",
        type=int,
        required=False,
        default=1,
        help="""Number of parallel chunks to process""")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help=
        """Don't execute any programs, just print what would have been run""")

    main(parser.parse_args())
