#!/usr/bin/env python3

import subprocess
import sys

import click

import libflavour


def log(string):
    click.echo(f"fam-aldryn: {string}")


def check_structure(yaml):
    libflavour.Addon(yaml)


def check_policies(yaml):

    process = subprocess.Popen(
        ["conftest", "test", "-p=/flavour/fam-aldryn/policy", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    process.stdin.write(str.encode(yaml))
    outs, errs = process.communicate()

    print(outs.decode("utf-8").strip())

    if process.returncode:
        if errs:
            print(errs.decode("utf-8").strip())
        sys.exit(process.returncode)
    process.stdin.close()


@click.command()
def check():
    yaml = click.get_text_stream("stdin").read()

    log("calling parent: /bin/fam-flavour/check")
    process = subprocess.Popen(
        ["/bin/fam-flavour/check"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    process.stdin.write(str.encode(yaml))
    outs, errs = process.communicate()

    print(outs.decode("utf-8").strip())

    if process.returncode:
        if errs:
            print(errs.decode("utf-8").strip())
        sys.exit(process.returncode)
    process.stdin.close()

    log("Check structure")
    check_structure(yaml)

    log("Check policies")
    check_policies(yaml)


if __name__ == "__main__":
    check()
