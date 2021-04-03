import argparse
import glob
import os
import sys


def automate(args):
    with open(os.path.abspath(f"{__file__}/../resources/make.py")) as script:
        script = script.read()
    with open(args.output, "w") as file:
        file.write(script)


def quickstart(template="new"):
    if template in ["new", "from_source"]:
        print(f"Ark Utility (Template '{template}')")
        print(
            "Leave the input empty if you do not want to give it,\n"
            "fields with this '*' are required"
        )

        print("\nBasic Information\n")
        inputs = [
            input("Name       *:"),
            input("Version    *:"),
            input("Description :"),
            input("Author      :"),
            input("Author Email:"),
            input("Github Name :"),
            input("Key Sign    :"),
        ]
        config = {
            "name": inputs[0],
            "version": inputs[1],
            "description": inputs[2],
            "author": inputs[3] if inputs[3] != "" else "Unknown",
            "author_email": inputs[4] if inputs[4] != "" else "Unknown",
            "github_name": inputs[5],
            "key_sign": inputs[6] if inputs[6] != "" else None,
        }
        from pios_sdk import app, ppk

        app.make_empty_app(**config)
        if template == "new":
            ppk.main(["config", "-o"])
        elif template == "from_source":
            print("\n\nFrom Source Configurations\n")
            inputs = [
                input("Main File            (main.py):"),
                input("Icon File           (icon.cpg):"),
                input("Installer (pios-sdk-installer):"),
            ]
            main_file = inputs[0] if inputs[0] != "" else "main.py"
            icon_file = inputs[1] if inputs[1] != "" else "icon.cpg"
            installer = (
                inputs[2]
                if inputs[2] != ""
                else os.path.abspath(f"{__file__}/../_installer.py")
            )
            print("\nAdd Data Files\n")
            add_files = []
            while True:
                temp = input("glob :")
                if temp == "":
                    break
                add_files.extend(glob.glob(temp))

            print("\nAdd Data Directories\n")
            add_directories = []
            while True:
                temp = input("glob :")
                if temp == "":
                    break
                add_directories.append(glob.glob(temp))

            print("\nAdd Local Modules\n")
            add_modules = []
            while True:
                temp = input("glob :")
                if temp == "":
                    break
                add_modules.append(glob.glob(temp))

            print("\nAdd Local Packages\n")
            add_packages = []
            while True:
                temp = input("glob :")
                if temp == "":
                    break
                add_packages.append(glob.glob(temp))

            print("\nAdd PyPI Requirements\n")
            add_pypi_packages = []
            while True:
                temp = input("requirement :")
                if temp == "":
                    break
                add_pypi_packages.append(temp)

            print("\nAdd SDK Packages")
            print("type 'list' to get a list of available sdk packages\n")
            add_sdk_packages = []
            sdk_packages = os.listdir(os.path.abspath(f"{__file__}/../library"))
            while True:
                temp = input("sdk :")
                if temp == "":
                    break
                elif temp == "list":
                    for x in sdk_packages:
                        print(x)
                    continue
                if temp in sdk_packages:
                    add_sdk_packages.append(temp)
                else:
                    print("No Such SDK Package (type 'list')")

            arguments = [
                "config",
                "-mf",
                main_file,
                "--icon",
                icon_file,
                "-i",
                installer,
                "-o",
            ]

            for x in add_files:
                arguments.extend(["-af", x])
            for x in add_directories:
                arguments.extend(["-ad", x])
            for x in add_packages:
                arguments.extend(["-p", x])
            for x in add_modules:
                arguments.extend(["-m", x])
            for x in add_pypi_packages:
                arguments.extend(["-r", x])
            for x in add_sdk_packages:
                arguments.extend(["-P", x])

            ppk.main(arguments)


def main(arguments: list = None):
    if arguments is None:
        arguments = sys.argv[1:]
    parser = argparse.ArgumentParser(
        "test", description="a small utility for creating automation script"
    )
    commands = parser.add_subparsers(dest="command", title="Commands", metavar="")

    quickstart_command = commands.add_parser(
        "quickstart", help="Quick Start with a PiOS Project"
    )
    quickstart_command.add_argument(
        "template",
        choices=["new", "from_source"],
        default="new",
        nargs="?",
        help="Template to quickstart from",
    )

    automate_command = commands.add_parser(
        "automate", help="Generate a setup.py file for your existing project"
    )
    automate_command.add_argument(
        "-o", "--output", help="Output file to write the code to", default="setup.py"
    )

    args = parser.parse_args(arguments)

    if args.command == "automate":
        automate(args)
    elif args.command == "quickstart":
        quickstart(args.template)


if __name__ == "__main__":
    main()
