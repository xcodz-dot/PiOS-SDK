import sys
from argparse import ArgumentParser
from hashlib import sha256


def generate_sha256(file):
    sha = sha256()
    while True:
        chunk = file.read(1024 * 1024)
        if not chunk:
            break
        sha.update(chunk)
    return sha.hexdigest()


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = ArgumentParser(description="Generate SHA-256 checksum with files")
    parser.add_argument("file", help="File to generate SHA-256")
    parser.add_argument(
        "output",
        help="(Optional) Write checksum to output, if not provided, prints to stdout",
        default=None,
        nargs="?",
    )
    args = parser.parse_args(args)
    fp = open(args.file, "rb")
    sha = generate_sha256(fp)
    fp.close()
    if args.output is None:
        print(sha)
    else:
        with open(args.output, "w") as file:
            file.write(sha)


if __name__ == "__main__":
    main()
