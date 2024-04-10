import argparse
from commands import fetch
import logging

def setup_parser():
     parser = argparse.ArgumentParser(description="Investment data CLI")
     subparsers = parser.add_subparsers(title="commands", dest="command")

     #  add subcommands from other modules
     fetch.setup_subparser(subparsers)


     return parser


def run():
      # Basic logging configuration
     logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

     parser = setup_parser()
     args = parser.parse_args()

     if args.command == "fetch":
         fetch.execute(args)

     else:
         parser.error("No command specified.")
     