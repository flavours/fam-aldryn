import os
import shutil


def get_start_and_end_tag(tag_name):
    return ("# <{}>".format(tag_name), "# </{}>".format(tag_name))


def replace_between_tags(source, data, tag_name, preserve_indentation=True):
    source = source or ""
    lines = source.split("\n")
    start_tag, end_tag = get_start_and_end_tag(tag_name)
    start = None
    end = None
    prefix = ""
    for index, line in enumerate(lines):
        if line.strip().startswith(start_tag):
            start = index
            if preserve_indentation:
                prefix = line[0 : len(line) - len(line.lstrip())]
        elif line.strip().startswith(end_tag):
            end = index
        if start is not None and end is not None:
            break

    if start is not None and end is not None:
        # make sure the data contains no trailing new lines
        data = data.rstrip("\n")
        content = ["{}{}".format(prefix, ln) for ln in data.split("\n")]
        lines[start : end + 1] = content
    return "\n".join(lines)


def extract_tag(
    source,
    tag_name,
    include_tags=False,
    strip_comments=None,
    strip_lines=False,
):
    if not source:
        return ""

    lines = source.split("\n")
    start_tag, end_tag = get_start_and_end_tag(tag_name)
    start = None
    end = None
    for index, line in enumerate(lines):
        if line.strip().startswith(start_tag):
            start = index
        elif line.strip().startswith(end_tag):
            end = index
        if start is not None and end is not None:
            break

    if start is None or end is None:
        return ""

    if include_tags:
        content = lines[start : end + 1]
    else:
        content = lines[start + 1 : end]
    cleaned_content = []
    for line in content:
        if strip_lines:
            line = line.strip()
            if not line:
                continue

        if strip_comments and line.strip()[0] in strip_comments:
            continue

        cleaned_content.append(line)
    return "\n".join(cleaned_content)


def write_file(path, content):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except OSError:
        print(path)
        raise

    # Guard against symlink attacks (we can probably handle this
    # more gracefully...)
    assert not os.path.islink(path)

    with open(path, "w+") as fobj:
        fobj.write(content)


def read_file(path):
    if os.path.isfile(path) and not os.path.islink(path):
        with open(path, "r+") as fobj:
            return fobj.read()

    return None


def get_prefered_quotation_from_string(string):
    """
    Tries to determin the quotation (`"` or `'`) used in a given string.
    `"` is the default and used when no quotations are found or
    the amount of `"` and `'` are equal
    """
    return "'" if string.count("'") > string.count('"') else '"'


def copydir(source, dest):
    """Copy a directory structure overwriting existing files"""
    for root, dirs, files in os.walk(source):
        if not os.path.isdir(root):
            os.makedirs(root)

        for file in files:
            rel_path = root.replace(source, "").lstrip(os.sep)
            dest_path = os.path.join(dest, rel_path)

            if not os.path.isdir(dest_path):
                os.makedirs(dest_path)

            shutil.copyfile(
                os.path.join(root, file), os.path.join(dest_path, file)
            )


def read_installed_addons(filename):
    if not os.path.exists(filename):
        raise RuntimeError(f"Can not find {filename}")
    old_requirements_in_full = read_file(filename)

    # Get the current installed addons as a list
    return extract_tag(
        old_requirements_in_full,
        "INSTALLED_ADDONS",
        strip_comments=("#",),
        strip_lines=True,
    ).split("\n")


def write_installed_addons(filename, installed_addons):
    if not os.path.exists(filename):
        raise RuntimeError(f"Can not find {filename}")
    old_requirements_in_full = read_file(filename)

    # Update the list
    installed_addons.insert(
        0,
        "# <INSTALLED_ADDONS>  # Warning: text inside the "
        "INSTALLED_ADDONS tags is auto-generated. Manual changes will "
        "be overwritten.",
    )
    installed_addons.append("# </INSTALLED_ADDONS>")

    # Write back the information into the file
    new_installed_addons = "\n".join(installed_addons)
    new_settings_py_full = replace_between_tags(
        old_requirements_in_full, new_installed_addons, "INSTALLED_ADDONS"
    )
    write_file(filename, new_settings_py_full)


# A couple of addons neeed special handling.
# These addons are called `system addons` and they rely on a special order.
SYSTEM_ADDONS = {
    "aldryn-addons": 1,
    "aldryn-django": 2,
    "aldryn-sso": 3,
    "aldryn-django-cms": 4,
    "aldryn-devsync": 5,
}


def sort_addons(unsorted_addons, quotation='"'):
    """
    Some django system addons need special handling.
    This function sorts the addons accordingly.

    First, the system addons will be added (according to their ordering) and
    the others will be alphabetically ordered.
    """
    sorted_addons = []

    for system_addon in SYSTEM_ADDONS:
        if f"{quotation}{system_addon}{quotation}," in unsorted_addons:
            sorted_addons.append(f"{quotation}{system_addon}{quotation},")
            del unsorted_addons[
                unsorted_addons.index(f"{quotation}{system_addon}{quotation},")
            ]

    unsorted_addons.sort()
    sorted_addons = sorted_addons + unsorted_addons

    return sorted_addons
