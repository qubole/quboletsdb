##
 # Copyright (c) 2015. Qubole Inc
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 #     http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 #    limitations under the License.
##
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
