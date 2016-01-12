#!/bin/env python
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
import ConfigParser
import os
import sys
import traceback
import logging
from parsers import setup_parsers
from qds_sdk.qubole import Qubole

def load_config(config_args):
    config_candidates = []
    if config_args.config:
        config_candidates.append(config_args.config)
    config_candidates.append(os.path.expanduser("~/.qdsrc"))

    config = ConfigParser.SafeConfigParser()
    files_read = config.read(config_candidates)
    if len(files_read) == 0:
        logging.warning("No configuration files found. Did you create ~/.qdsrc ?")
    return config


def main():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # I am using this slightly complicated trick to pass config in the constructor of
    # other packages. Better way to do this ?

    config_parser, argparser = setup_parsers()

    config_args, remaining_argv = config_parser.parse_known_args()
    config = load_config(config_args)

    args = argparser.parse_args(remaining_argv)

    if args.debug:
        ch.setLevel(logging.DEBUG)
        root.setLevel(logging.DEBUG)
        logging.debug("Debug is ON!")
    if args.log_file is not None:
        fh = logging.FileHandler(args.log_file, mode='w')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        root.setLevel(logging.DEBUG)
        root.addHandler(fh)
    try:
        Qubole.configure(
            api_token=config.get("default", "auth_token"),
            api_url=config.get("default", "api_url"),
            skip_ssl_cert_check=True
        )
        args.func(config, args)
    finally:
        logging.debug("Cleaning up")


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc(file=sys.stderr)
        sys.exit(3)
