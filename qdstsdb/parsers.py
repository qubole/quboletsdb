__author__ = 'rajatv'

import argparse
from qdstsdb import __version__
from cluster import Cluster


def setup_parsers():
    config_parser = argparse.ArgumentParser(description="Operate and manage opentsdb on Qubole Data Service.", add_help=False)
    config_parser.add_argument("-c", "--config", help="Path to configuration file", metavar="FILE")
    config_parser.add_argument("-v", "--version", action='version', version=__version__)

    argparser = argparse.ArgumentParser(description="Operate and manage opentsdb on Qubole Data Service.",
                                        parents=[config_parser])
    debug_group = argparser.add_mutually_exclusive_group()
    debug_group.add_argument("-d", "--debug", action="store_true", default=False,
                             help="Turn on debug logging and print to stdout")
    debug_group.add_argument("-x", "--log", dest="log_file",
                             help="Turn on debug logging and print to log file")

    subparsers = argparser.add_subparsers()
    Cluster.setup_parser(subparsers)

    return config_parser, argparser