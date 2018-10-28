"""
This is the runner, entrypoint to CheapCaller application
"""
import sys
import json

from cheap_caller import parser
from cheap_caller import helpers


def main():
    """The main function which gets called when this script is invoked
    """
    args = parser.parse(sys.argv[1:])
    # Read the logging conf file
    helpers.read_logging_conf_file()
    # Configure the logger
    logger = helpers.configure_logger(
        "cheap_caller",
        args.get("log_level"),
    )
    # Sanitize phone number(strip +, 00, -)
    # Exit if invalid
    try:
        phoneno = helpers.sanitize_and_validate_phoneno(
            args.get("phoneno")
        )
    except ValueError as error:
        logger.debug(
            "The actual exception raised: %s",
            str(error), exc_info=True
        )
        logger.error(
            "Phone number can only have +(only leading), - and digits, "
            "%s is not valid, exiting", args.get("phoneno")
        )
        sys.exit(1)
    # Get all the extensions starting from the full phonenumber
    # working backwards to the first digit in phone number
    extensions = helpers.gen_right_triangle(phoneno)
    # Operator data processing pipeline
    # find all the operator files
    filepaths = helpers.gen_find(
        args.get("pattern"),
        args.get("operatordir")
    )
    # dictseq is a generator which yields a sequence of dicts
    # each dict has two items {"name": operator name, "source": sequence of fileobj}
    dictseq = helpers.open_files(filepaths)
    # each dict now has two items {"name": operator name, "source": sequence of lines}
    dictseq = helpers.map_from_fileobj_to_lines(dictseq)
    # We get the cheapest per operator
    cheapest_per_operator = helpers.get_cheapest_per_operator(
        dictseq,
        extensions
    )
    if not cheapest_per_operator:
        logger.error("No match for given number in any operators, exiting")
        sys.exit(1)
    logger.info(
        "Cheapest per operator: %s",
        json.dumps(cheapest_per_operator, indent=4)
    )
    # We get the cheapest overall
    cheapest_operator, price = helpers.get_cheapest(cheapest_per_operator)
    logger.info(
        "Cheapest overall for no: %s"
        " is operator: %s and price: %s",
        phoneno, cheapest_operator, price
    )


if __name__ == "__main__":
    main()
