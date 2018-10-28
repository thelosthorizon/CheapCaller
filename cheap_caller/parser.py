"""
This module handles the parsing of command line args
"""
import os
import argparse

def parse(args):
    """Handles the parsing of command line arguments

    Keyword Arguments:
        args {list} -- list of arguments/values

    Returns:
        dict -- dict containing parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Find the cheapest operator to call with.'
    )
    parser.add_argument(
        "phoneno",
        metavar="<phonenumber>",
        action="store",
        help="""
            Phone number that you would like to call.
            """
    )
    parser.add_argument(
        "operatordir",
        action="store",
        metavar="<directory>",
        help="""
            Path to top level of a directory where to look for
            operator files.
            """
    )
    parser.add_argument(
        "--pattern",
        "-p",
        metavar="<pattern>",
        action="store",
        default="*.operator",
        help="""
            The pattern used when looking for operator files.
            """
    )
    parser.add_argument(
        "--log-level",
        "-ll",
        metavar="<log_level>",
        action="store",
        default="info",
        choices=("debug", "info", "warning", "error", "critical"),
        help="""
            Log level that will be used when logging to screen.
            """
    )
    parsed = parser.parse_args(args)
    parsed = vars(parsed)
    if not os.path.exists(parsed["operatordir"]):
        parser.error("operatordir has to be a valid directory")
    return parsed
