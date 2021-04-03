"""
PiOS Package Kit
================

The Official Build Tools for PiOS
"""

import argparse
import copy
import json
import os
import pickle
import shutil
import sys
from collections import OrderedDict

import toml


def remove_duplicates(d: list):
    r = list(OrderedDict.fromkeys(d))
    d.clear()
    d.extend(r)


class PPK:
    def __init__(self):
        self.config = None
        self.installer = None
        self.packages = []
        self.py_modules = []
        self.data_directories = []
        self.data_files = []
        self.main_package = "main"
        self.requirement = []
        self.sdk_packages = []

    def add_directory(self, directory):
        self.data_directories.append(directory)

    def set_configuration(self, configuration_file):
        with open(configuration_file) as file:
            self.config = json.load(file)

    def set_custom_installer(self, installer_file):
        with open(installer_file) as file:
            self.installer = file.read()

    def add_package(self, package):
        self.packages.append(package)

    def add_sdk_package(self, name):
        self.sdk_packages.append(name)

    def add_file(self, file):
        self.data_files.append(file)

    def add_module(self, module):
        self.py_modules.append(module)

    def add_pip_requirement(self, requirement, update=False, pre=False):
        self.requirement.append((requirement, pre, update))

    def set_main_package(self, package):
        self.main_package = package

    def build(self):
        with open(os.path.abspath(f"{__file__}/../library.toml")) as file:
            library_configuration = toml.load(file)
        print(".", flush=True, end="")
        if "pios_build" in os.listdir():
            shutil.rmtree("pios_build")
        os.mkdir("pios_build")
        os.mkdir("pios_build/assets")
        with open("pios_build/setup.py", "w") as file:
            file.write(self.installer)
        with open("pios_build/app.json", "w") as file:
            json.dump(self.config, file, indent=4, sort_keys=True)
        with open("pios_build/requirements.pickle", "w+b") as file:
            r = copy.copy(self.requirement)
            for package in self.sdk_packages:
                r.extend(library_configuration[package]["requires"])
            pickle.dump(r, file)
        for x in self.data_directories:
            shutil.copytree(x, f"pios_build/assets/{os.path.basename(x)}")
        for x in self.data_files:
            shutil.copyfile(x, f"pios_build/assets/{os.path.basename(x)}")
        for x in self.packages:
            shutil.copytree(x, f"pios_build/packages/{os.path.basename(x)}")
        packages_required = copy.copy(self.sdk_packages)
        for x in self.sdk_packages:
            packages_required.extend(library_configuration[x]["uses"])
        packages_required = list(set(packages_required))
        for x in packages_required:
            shutil.copytree(
                os.path.abspath(f"{__file__}/../library/{x}"),
                f"pios_build/packages/{os.path.basename(x)}",
            )
        for x in self.py_modules:
            shutil.copyfile(x, f"pios_build/packages/{os.path.basename(x)}")
        shutil.copyfile(self.main_package, "pios_build/main.py")

    @staticmethod
    def package():
        if os.path.isfile("pios_build/ppk.zip"):
            os.remove("pios_build/ppk.zip")
        if "dist" not in os.listdir():
            os.mkdir("dist")
        shutil.make_archive("pios_build/ppk", "zip", "pios_build")
        shutil.copyfile("pios_build/ppk.zip", "dist/app-main.ppk")

    def load_using_toml(self, file="build.toml"):
        with open(file) as file:
            config = toml.load(file)
        build_config = config["build"]
        self.set_main_package(build_config["files"]["main"])
        self.set_custom_installer(build_config["files"]["installer"])
        self.set_configuration(build_config["files"]["configuration"])
        for x in build_config["dependencies"]["pypi"]:
            self.add_pip_requirement(x)
        for x in build_config["dependencies"]["sdk"]:
            self.add_sdk_package(x)
        for x in build_config["dependencies"]["local_packages"]:
            self.add_package(x)
        for x in build_config["dependencies"]["local_modules"]:
            self.add_module(x)
        for x in build_config["data"]["files"]:
            self.add_file(x)
        for x in build_config["data"]["directories"]:
            self.add_directory(x)

    def load_using_json(self, file="build.json"):
        with open(file) as file:
            config = json.load(file)
        self.set_main_package(config["main_module"])
        self.set_custom_installer(config["installer"])
        self.set_configuration(config["configuration"])
        for x in config["requirements"]:
            self.add_pip_requirement(x)
        for x in config["data_files"]:
            self.add_file(x)
        for x in config["data_directories"]:
            self.add_directory(x)
        for x in config["packages"]:
            self.add_package(x)
        for x in config["modules"]:
            self.add_module(x)
        for x in config["sdk_packages"]:
            self.add_sdk_package(x)


def main(arguments=None):
    if arguments is None:
        arguments = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="PPK Package Tool", fromfile_prefix_chars="@"
    )
    subparser = parser.add_subparsers(title="Commands", dest="command_", metavar="")
    options = parser.add_mutually_exclusive_group()
    options.add_argument(
        "-l",
        "--list-sdk-packages",
        help="lists packages that come with sdk",
        action="store_true",
    )
    setup_modifier = subparser.add_parser("config", help="Configure the project")
    setup_modifier.add_argument(
        "-p",
        "--package",
        help="add a python package to build list",
        action="append",
        default=None,
    )
    setup_modifier.add_argument(
        "-o",
        "--overwrite",
        help="Overwrite the existing configuration file",
        action="store_true",
    )
    setup_modifier.add_argument(
        "-P",
        "--sdk-package",
        help="add a local copy of sdk library to packages",
        action="append",
        default=None,
    )
    setup_modifier.add_argument(
        "-m",
        "--module",
        help="add a python module to build list",
        action="append",
        default=None,
    )
    setup_modifier.add_argument(
        "-r",
        "--pypi-requirement",
        help="add a python pypi package to build list",
        action="append",
        default=None,
    )
    setup_modifier.add_argument(
        "-ad",
        "--add-directory",
        help="add a directory to build list",
        action="append",
        default=None,
    )
    setup_modifier.add_argument(
        "-af",
        "--add-file",
        help="add a file to to build list",
        action="append",
        default=None,
    )
    setup_modifier.add_argument(
        "-i", "--installer", help="add a custom installer to build list", default=None
    )
    setup_modifier.add_argument(
        "-c",
        "--configure",
        help="add a app configuration to build list",
        default=None,
    )
    setup_modifier.add_argument(
        "-mf", "--main-file", help="set a main file", default=None
    )
    options.add_argument(
        "-b",
        "--build",
        help="Build the ppk using 'build.toml' file",
        action="store_true",
    )
    options.add_argument(
        "-p",
        "--pios-package-kit",
        help="Packages the final app into PPK",
        action="store_true",
    )
    options.add_argument(
        "-c",
        "--cleanup",
        help="Cleanup the directory be deleting unnecessary data",
        action="store_true",
    )

    args = parser.parse_args(arguments)

    if args.list_sdk_packages:
        with open(os.path.abspath(f"{__file__}/../library.toml")) as file:
            lib_info = toml.load(file)
        for x in lib_info.keys():
            newline = "\n"
            print(
                f"""
{x} :: r{lib_info[x]["revision"]}
    {lib_info[x]["help"]}

    {(f'uses:{newline+" "*8}'+(newline+' '*8).join(lib_info[x]['uses'])) if lib_info[x]['uses'] != [] else 'uses: None'}
    {(f'requires:{newline+" "*8}'+(newline+' '*8).join(lib_info[x]['requires'])) if lib_info[x]['requires'] != []
                else 'requires: None'}"""
            )
    elif args.build:
        app = PPK()
        app.load_using_toml()
        app.build()
    elif args.cleanup:
        if "pios_build" in os.listdir():
            shutil.rmtree("pios_build")
    elif args.pios_package_kit:
        app = PPK()
        app.load_using_toml()
        app.package()
    elif args.command_ == "config":
        if args.overwrite or (not os.path.isfile("build.toml")):
            if args.installer is None:
                args.installer = os.path.abspath(
                    f"{__file__}/../_installer.py"
                ).replace(os.sep, "/")
            else:
                args.installer = args.installer.replace(os.sep, "/")
            if args.main_file is None:
                args.main_file = "main.py"
            if args.configure is None:
                args.configure = "app.json"

            if args.pypi_requirement is None:
                args.pypi_requirement = []
            if args.sdk_package is None:
                args.sdk_package = []
            if args.module is None:
                args.module = []
            if args.package is None:
                args.package = []
            if args.add_file is None:
                args.add_file = []
            if args.add_directory is None:
                args.add_directory = []
            config = {
                "build": {
                    "files": {
                        "icon": args.icon,
                        "main": args.main_file,
                        "configuration": args.configure,
                        "installer": args.installer,
                    },
                    "dependencies": {
                        "pypi": args.pypi_requirement,
                        "sdk": args.sdk_package,
                        "local_modules": args.module,
                        "local_packages": args.package,
                    },
                    "data": {"files": args.add_file, "directories": args.add_directory},
                }
            }
        elif args.command_ == "config":
            with open("build.toml", "r") as file:
                config = toml.load(file)
            if args.main_file:
                config["build"]["files"]["main"] = args.main_file
            if args.configure:
                config["build"]["files"]["configuration"] = args.configure
            if args.installer:
                config["build"]["files"]["installer"] = args.installer

            if args.pypi_requirement:
                config["build"]["dependencies"]["pypi"].extend(args.pypi_requirement)
            if args.sdk_package:
                config["build"]["dependencies"]["sdk"].extend(args.sdk_package)
            if args.package:
                config["build"]["dependencies"]["local_packages"].extend(args.package)
            if args.module:
                config["build"]["dependencies"]["local_modules"].extend(args.module)

            if args.add_file:
                config["build"]["data"]["files"].extend(args.add_file)
            if args.add_directory:
                config["build"]["data"]["directories"].extend(args.add_directory)

        # Code for removal of duplicates
        remove_duplicates(config["build"]["data"]["files"])
        remove_duplicates(config["build"]["data"]["directories"])
        remove_duplicates(config["build"]["dependencies"]["pypi"])
        remove_duplicates(config["build"]["dependencies"]["sdk"])
        remove_duplicates(config["build"]["dependencies"]["local_packages"])
        remove_duplicates(config["build"]["dependencies"]["local_modules"])

        for x in config["build"]["data"]["files"]:
            if not os.path.isfile(x):
                print(
                    f"Warning: data_file: '{x}' does not exist but is added to configuration"
                )
        for x in config["build"]["data"]["directories"]:
            if not os.path.isdir(x):
                print(
                    f"Warning: data_directory: '{x}' does not exist but is added to configuration"
                )
        for x in config["build"]["dependencies"]["local_packages"]:
            if not os.path.isdir(x):
                print(
                    f"Warning: local_package: '{x}' does not exist but is added to configuration"
                )
        for x in config["build"]["dependencies"]["local_modules"]:
            if not os.path.isfile(x):
                print(
                    f"Warning: local_module: '{x}' does not exist but is added to configuration"
                )

        with open("build.toml", "w") as file:
            toml.dump(config, file)


if __name__ == "__main__":
    main(sys.argv[1:])
