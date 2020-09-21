#!/usr/bin/env python
"""parser.py: handles cli parsing."""

import argparse
import ctypes

def parse_arguments():
    
    parser = argparse.ArgumentParser(
        description='Audio recorder script'
    )
    # Verbose logging
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', help='set logger to debug.')
    # Chunk size (sample count)
    parser.add_argument('-CS', '--CHUNK_SIZE', dest='CHUNK_SIZE', default=4096,
                        type=int, help='Chunk size. number of samples within each chunk.')
    # sample rate each sec
    parser.add_argument('-SR', '--SAMPLE_RATE', dest='SAMPLE_RATE', default=44100,
                        type=int, help='Sample rate in Hz.')

    return parser.parse_args()
