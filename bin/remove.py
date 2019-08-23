#!/usr/bin/env python3

import shutil
import subprocess
import sys

import click

import libflavour
from fam_diviocloud_addon import constants, utils
from strictyaml import load


# Add the ptdraft folder path to the sys.path list
sys.path.append("/usr/lib/")


def log(string):
    click.echo(f"fam-diviocloud-addon: {string}")


def update_requirements_in(addon_name):
    installed_addons = utils.read_installed_addons(constants.REQUIREMENTS_FILE)
    try:
        installed_addons.remove(addon_name)
    except ValueError:
        pass
    utils.write_installed_addons(constants.REQUIREMENTS_FILE, installed_addons)


def update_settings_py(addon_name):
    old_settings_py_full = utils.read_file(constants.SETTINGS_FILE)
    quotation = utils.get_prefered_quotation_from_string(old_settings_py_full)

    installed_addons = utils.read_installed_addons(constants.SETTINGS_FILE)
    try:
        installed_addons.remove(f"{quotation}{addon_name}{quotation},")
    except ValueError:
        pass
    utils.write_installed_addons(constants.SETTINGS_FILE, installed_addons)


def remove_addons_folder(addon_name):

    shutil.rmtree(f"/app/addons/{addon_name}")


@click.command()
def remove():
    yaml = click.get_text_stream("stdin").read()

    log("calling parent: /bin/fam-flavour/remove")
    process = subprocess.Popen(
        ["/bin/fam-flavour/remove"],
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

    yaml_data = load(yaml, libflavour.schema.schema_addon)
    log(f"removing: {yaml_data['meta']['name']}")

    log("Updating requirements.in")
    update_requirements_in(str(yaml_data["install"]["artifact"]))

    log("Updating settings.py")
    update_settings_py(str(yaml_data["install"]["addonname"]))

    log("Removing addons folder")
    remove_addons_folder(str(yaml_data["install"]["addonname"]))


if __name__ == "__main__":
    remove()
