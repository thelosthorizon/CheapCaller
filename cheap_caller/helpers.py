"""
All the helpers functions are here
"""

import os
import logging
import logging.config
import json
import fnmatch


LOGGER = logging.getLogger(__name__)

def read_logging_conf_file(conf_file_path=None):
    """Read logging configuration from a file

    Keyword Arguments:
        conf_file_path {str} -- path to logging conf file (default: {None})
    """
    dafault_conf_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'logging_conf.json'
        )
    )
    if not conf_file_path:
        conf_file_path = dafault_conf_file
        LOGGER.debug(
            "Using default logging conf file: %s",
            conf_file_path
        )
    else:
        if not os.path.exists(conf_file_path):
            LOGGER.error(
                "Could not open given conf file: %s, "
                "using default: %s",
                conf_file_path, dafault_conf_file
            )
            conf_file_path = dafault_conf_file

    with open(conf_file_path) as logging_conf:
        logging.config.dictConfig(json.load(logging_conf))


def configure_logger(logger_name, log_level):
    """To configure a logger with a given name and level

    Note:
    logger_name is one of the loggers in the logging conf file.
    This only changes log level of the stream handler,
    and not the logger itself, which is always debug,
    so the logger is very permissive, stream handler is not.
    All the debug log lines always get written to debug.log file

    Arguments:
        logger_name {str} -- logger name
        log_level {str} -- log level string
        ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

    Returns:
        obj -- logger object returned by logger.getLogger
    """

    logger = logging.getLogger(logger_name)
    numeric_level = getattr(
        logging,
        log_level.upper(),
        logger.handlers[0].level
    )
    logger.handlers[0].setLevel(numeric_level)
    return logger

def remove_leading_plus_and_zeros(string_to_be_curated):
    """Strip leading + sign and 00 seen in phone number and extension

    Arguments:
        string_to_be_curated {string} -- input phone number

    Returns:
        string -- stripped off string(no leading + and 00)
    """
    string_to_be_curated = string_to_be_curated.strip()
    zipped = zip(["00", "+"], ["+", "00"])
    for val in zipped:
        if string_to_be_curated.startswith(val[0]):
            string_to_be_curated = string_to_be_curated.split(val[0], 1)[-1]
            if string_to_be_curated.startswith(val[1]):
                string_to_be_curated = string_to_be_curated.split(val[1], 1)[-1]
    return string_to_be_curated

def gen_right_triangle(input_string):
    """Builds a list containing elements that builds right triangle
    12345 would be:
    12345
    1234
    123
    12
    1

    Arguments:
        input_string {str} -- input string

    Returns:
        list -- list with all possible extensions
        e.g. a 12345 would return [12345, 1234, 123, 12, 1]
    """
    out = [
        input_string[:index] for index in xrange(1, len(input_string)+1)
    ]
    return out[::-1]

def sanitize_and_validate_phoneno(phoneno):
    """Sanitize a phone number, strips off +, - and 00

    Arguments:
        phoneno {str} -- phone number

    Returns:
        str -- sanitized phone number
    """
    if not phoneno:
        raise ValueError("No phoneno provided")
    # strip leading + and 00
    phoneno = remove_leading_plus_and_zeros(phoneno)
    # remove - from the phoneno
    phoneno = "".join(phoneno.split("-"))
    float(phoneno)
    # This will raise ValueError if invalid number
    return phoneno

def gen_find(filepat, top):
    """Find all files in a directory tree(recursively) matching a pattern

    Arguments:
        filepat {str} -- pattern to match
        top {str} -- path to start from
    """
    for path, _, filelist in os.walk(top):
        for name in fnmatch.filter(filelist, filepat):
            LOGGER.debug("Found a file: %s matching: %s", name, filepat)
            yield os.path.join(path, name)

def open_files(file_paths):
    """Open files in the input sequence and
    yield a sequence of dicts each dict has two items:
        name = operatorname
        source = open file object

    Arguments:
        file_paths {obj} -- a sequence of full file paths
    """
    for file_path in file_paths:
        if not os.path.exists(file_path):
            LOGGER.error("Failed to open: %s, ignoring", file_path)
            continue
        name = os.path.splitext(
            os.path.basename(file_path)
        )[0]
        with open(file_path) as opened_file:
            yield {
                "name": name,
                "source": opened_file
            }

def gen_lines(name, source):
    """Strip each line and split using "," delimeter from an open fileobj,
    validate comma separated values are digits and yields sequence of lists,
    each list is the splitted line

    Arguments:
        name {str} -- file name (used only for logging)
        source {obj} -- an open fileobj
    """
    for line in source:
        # strip any space in the beginning and end
        line = line.strip()
        # We only care about first two values
        line_splitted = line.split(",")[:2]
        if not len(line_splitted) == 2:
            LOGGER.warning(
                "Ignoring %s line in %s,"
                " not a comma separated extension and price",
                line, name
            )
            continue
        line_splitted[0] = remove_leading_plus_and_zeros(
            line_splitted[0]
        )
        # strip the second part to remove any leading space
        line_splitted[1] = line_splitted[1].lstrip()
        try:
            [float(val) for val in line_splitted]
        except ValueError:
            # To ignore invalid lines
            LOGGER.warning(
                "Ignoring %s line in %s,"
                " not a comma separated extension and price",
                line, name
            )
            continue
        yield line_splitted

def map_from_fileobj_to_lines(dictseq):
    """Map fileobj in "source" item for each dict in dictseq
    to sequence of lines returned by gen_lines()

    Arguments:
        dictseq {obj} -- sequence of dicts
    """
    for a_dict in dictseq:
        # "source" field now is sequence of lines
        a_dict["source"] = gen_lines(a_dict["name"], a_dict["source"])
        yield a_dict


def get_cheapest_per_operator(dictseq, extensions):
    """Get cheapest call rate per operator for a given phoneno

    Filter sequence of lines in "source" item for each dict in dictseq
    using each extension in extensions and return a dict containing
    cheapest rate per operator

    Arguments:
        dictseq {obj} -- sequence of dict
        extensions {list} -- list containing extensions
                             returned by gen_right_triangle()

    Returns:
        dict -- multiple items, each item represents an operator
                key = operator name; value = call rate
    """
    cheapest_per_operator = {}
    # Check for each operator data
    for adict in dictseq:
        # adict represents an operator
        name = adict.get("name")
        # Have to use list() or we cant loop over each extension
        lines = list(adict["source"])
        for extension in extensions:
            matching = [
                line for line in lines if line[0] == extension
            ]
            # since we start from phone number and work our way back
            # to first digit, we can break if matching is non-empty
            # and work with another operator dict data
            if matching:
                LOGGER.debug(
                    "Matching lines for operator: %s, extension: %s, lines: %s",
                    name, extension, matching
                )
                # get the minimum value
                cheapest_per_operator[name] = min(
                    matching, key=lambda i: i[1]
                )
                break
    return cheapest_per_operator

def get_cheapest(adict):
    """Get cheapest operator and rate for a given phoneno

    Arguments:
        adict {dict} -- dict returned by get_cheapest_per_operator()

    Returns:
        tuple -- cheapest operatorname and call rate
    """
    # get the cheapest prices
    cheapest_price = min(adict.values(), key=lambda i: i[1])
    # find that value in the dict
    # return tuple -- (operator, price)
    for key, value in adict.iteritems():
        if value == cheapest_price:
            return (key, value[1])
