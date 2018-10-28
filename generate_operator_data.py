import os
import sys
import random
import argparse

def main(operator_name, number=1000):
    file_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        ".".join([operator_name, "operator"])
    )
    with open(file_path, 'a') as the_file:
        for _ in xrange(number):
            extension = "".join(
                random.sample("0123456789", random.randint(1, 5))
            )
            price = ".".join(
                [
                    "0",
                    "".join(
                        random.sample(
                            "0123456789", random.randint(1, 5)
                        )
                    )
                ]
            )
            the_file.write(
                "".join([",".join([extension, price]), "\n"])
            )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Generate an operator txt file with desired number of entries"
    )
    parser.add_argument(
        "name",
        metavar="<operatorname>",
        action="store",
        help="""
            Name of the operator, a txt file will be saved in data folder with
            the name.
            """
        )
    parser.add_argument(
        "--number",
        "-n",
        metavar="<number>",
        type=int,
        default=1000,
        help="""
            Number of entries.
            """
        )
    parsed = vars(
        parser.parse_args(sys.argv[1:])
    )
    main(
        parsed["name"],
        parsed["number"]
    )
