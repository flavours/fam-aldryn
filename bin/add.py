#!/usr/bin/env python3


import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import click

import libflavour
import requests


# Add the ptdraft folder path to the sys.path list
sys.path.append("/usr/lib/")
from fam_aldryn import constants, utils  # isort:skip


def log(string):
    click.echo(f"fam-aldryn: {string}")


def update_requirements_in(addon_name):
    """
    Tries to add update the requirements.in file and adds the `addon_name` to
    the INSTALLED_ACTIONS section.
    """

    installed_addons = utils.read_installed_addons(constants.REQUIREMENTS_FILE)
    installed_addons.append(addon_name)
    utils.write_installed_addons(constants.REQUIREMENTS_FILE, installed_addons)


def update_settings_py(addon_name):
    """
    Adds the addon name to the INSTALLED_ADDONS section.
    """

    old_settings_py_full = utils.read_file(constants.SETTINGS_FILE)
    quotation = utils.get_prefered_quotation_from_string(old_settings_py_full)

    installed_addons = utils.read_installed_addons(constants.SETTINGS_FILE)

    # Check if the addon maybe already exist and only act if it does not
    if f"{quotation}{addon_name}{quotation}," not in installed_addons:
        installed_addons.append(f"{quotation}{addon_name}{quotation},")
        sorted_installed_addons = utils.sort_addons(
            installed_addons, quotation=quotation
        )
        utils.write_installed_addons(
            constants.SETTINGS_FILE, sorted_installed_addons
        )


def copy_files_from_artifact(url):
    """
    Gets the artifact and copies some files from the artifact into the
    project for te installation.
    """

    copy_files = ["settings.json", "aldryn_config.py", "addon.json"]
    copy_folders = ["templates", "static"]

    r = requests.get(url)
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file_p = Path(temp_file.name)
        with temp_file_p.open("wb") as f:
            f.write(r.content)

        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(str(temp_file_p), "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            folder = [
                name
                for name in os.listdir(str(temp_dir))
                if os.path.isdir(os.path.join(str(temp_dir), name))
            ]
            assert len(folder) == 1
            package_folder_name = folder[0]

            addon_json_file = (
                Path(temp_dir)
                / package_folder_name
                / ".flavour"
                / "addon.json"
            )
            with addon_json_file.open("r") as f:
                addon_json_data = json.load(f)

            installed_apps = addon_json_data["installed-apps"]
            addon_name = addon_json_data["package-name"]

            # copy files
            for f in copy_files:
                p = Path(temp_dir) / package_folder_name / ".flavour" / f
                p_target_folder = Path("/app") / "addons" / addon_name
                p_target_folder.mkdir(parents=True, exist_ok=True)
                p_target = Path("/app") / "addons" / addon_name / f
                shutil.copy(str(p), p_target)

            for package_name in installed_apps:
                for f in copy_folders:
                    p = Path(temp_dir) / package_folder_name / package_name / f
                    p_target = Path("/app") / f
                    utils.copydir(str(p), str(p_target))


def fuzzy_check_if_addon_already_exists(yaml_data, fail):
    lines = utils.read_file(constants.REQUIREMENTS_FILE)

    for line in lines.split("\n"):
        # We check for the name of the addon file name without the version: */<addon-name>-*
        if f"/{yaml_data['install']['addonname']}-" in line:
            if fail:
                raise RuntimeError(
                    f"Addon already found in {constants.REQUIREMENTS_FILE}"
                )
            else:
                return False

    return True


@click.command()
def add():

    yaml = click.get_text_stream("stdin").read()
    yaml_data = libflavour.Addon(yaml)._data

    fuzzy_check_if_addon_already_exists(yaml_data, fail=True)

    log("calling parent: /bin/fam-flavour/add")
    process = subprocess.Popen(
        ["/bin/fam-flavour/add"], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    process.stdin.write(str.encode(yaml))
    outs, errs = process.communicate()

    print(outs.decode("utf-8").strip())

    if process.returncode:
        if errs:
            print(errs.decode("utf-8").strip())
        sys.exit(process.returncode)
    process.stdin.close()

    log(f"installing: {yaml_data['meta']['name']}")

    log("Updating requirements.in")
    update_requirements_in(str(yaml_data["install"]["artifact"]))

    log("Updating settings.py")
    update_settings_py(str(yaml_data["install"]["addonname"]))

    log("Copying files from package")
    copy_files_from_artifact(str(yaml_data["install"]["artifact"]))


if __name__ == "__main__":
    add()
