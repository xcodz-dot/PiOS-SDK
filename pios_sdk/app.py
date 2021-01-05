import argparse
import json
import os
import shutil
import sys
from typing import Tuple


class ConfigurationError(Exception):
    pass


def configuration_tuple(obj: str) -> Tuple[str]:
    return tuple(obj.split("=", 1))


required_configuration = [
    "name",
    "version",
]


def make_empty_app(**configuration):
    config = {
        "name": "",
        "version": "",
        "description": "",
        "author": "Unknown",
        "author_email": "Unknown",
        "github_name": "",
        "key_sign": None,
    }
    config.update(configuration)
    with open("app.json", "w") as file:
        json.dump(config, file, indent=4, sort_keys=True)
    for x in required_configuration:
        if x not in configuration.keys():
            raise ConfigurationError(
                f"The following configuration value is needed: {x}"
            )
    shutil.copyfile(os.path.abspath(f"{__file__}/../resources/main.py"), "main.py")
    shutil.copyfile(os.path.abspath(f"{__file__}/../resources/icon.cpg"), "icon.cpg")


def main(arguments=None):
    if arguments is None:
        arguments = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Generate PiOS Project", fromfile_prefix_chars="@"
    )
    parser.add_argument(
        "-n", "--new", help="Generate empty project", action="store_true"
    )
    parser.add_argument(
        "-c",
        "--configure",
        help="Configure a project with key value pair",
        action="append",
        type=configuration_tuple,
        default=[],
    )
    args = parser.parse_args(arguments)

    if args.new:
        make_empty_app(**{key: value for (key, value) in args.configure})


if __name__ == "__main__":
    main(sys.argv[1:])
