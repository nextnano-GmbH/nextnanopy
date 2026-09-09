def is_variable(text, var_char):
    boolean = False
    text = str(text).strip()
    if not text:
        boolean = False
    elif text[0] == var_char and "=" in text:
        boolean = True
    return boolean


def parse_variable(text, var_char, com_char):
    text = str(text).strip()
    if text[0] == var_char:
        text = str(text[1:])
    name, right = text.split("=", maxsplit=1)
    if com_char in right:
        value, comment = right.split(com_char, maxsplit=1)
    else:
        value = right
        comment = ""
    name, value, comment = [_str.strip() for _str in [name, value, comment]]
    value = autofmt_variable_value(value)
    return name, value, comment


def autofmt_variable_value(value):
    cases = [int, float, str]
    for case in cases:
        try:
            value = case(value)
            break
        except (ValueError, TypeError):
            pass
    return value


def pattern_in_text(text, input_pattern):
    if input_pattern in text:
        return True
    return False


def generate_command(args):
    cmd = []
    for case in args:
        arg, value = case
        _a, _v = _bool(arg), _bool(value)
        if not _a:
            continue
        elif _a and not _v:
            cmdi = f"{arg}"
        else:
            cmdi = f"{arg} {value}"
        cmd.append(cmdi)
    cmd = " ".join(cmd)
    return cmd


def text(init="", mid="", end="", fmt=lambda i, m, f: i + m + f):
    return fmt(str(init), str(mid), str(end))


def text_to_lines(text):
    yield from str(text).split("\n")


def lines_to_text(*lines):
    ls = "\n".join([str(t) for t in lines])
    return ls


def modify_lines_in_text(init="", mid="", end=""):
    ls = text_to_lines(mid)
    new = [text(init, line, end) for line in ls]
    return lines_to_text(*new)


def paragraph(content):
    return text("\n", content, "\n")


def preview(text, nums=True):
    lines = text_to_lines(text)
    for i, line in enumerate(lines):
        if nums:
            print(f"{i} {line}")
        else:
            print(f"{line}")


def _path(path):
    if path:
        path = rf"{path}"
        path = f'"{path}"'
    return path


def _bool(_in):
    if _in == 0:
        return True
    else:
        return bool(_in)


def split_by_pattern(_str, init, end):
    _str = str(_str)
    _l = []

    if init not in _str and end not in _str:
        return _l

    find_init = True
    str_old = str(_str)
    while True:
        if init not in str_old or end not in str_old:
            break
        if find_init:
            if init in str_old:
                find_init = False
        else:
            if end in str_old:
                idx_end = str_old.find(end) + 1
                _l.append(str_old[0:idx_end])
                str_old = str_old[idx_end:]
                find_init = True
    return _l


def str_to_name_unit(_str, init="[", end="]", default_unit=None, add_rest_to_name=False):
    if init in _str and end in _str:
        splitted = _str.split(init)
        name = splitted[0]
        rest = splitted[1]
        tail = rest.split(end)
        unit, rest = tail[0], tail[1:]
        name = name.strip()
        unit = unit.strip()
        if add_rest_to_name:
            name += "".join(rest)
            name = name.strip()
    else:
        name = str(_str).strip()
        unit = default_unit
    return name, unit


def str_to_name_unit_with_rest(_str, init, end, default_unit=None):
    """For the weird definition like 'psi[eV]_real' and 'psi[eV]_imag'"""
    name, unit = str_to_name_unit(_str, init, end, default_unit, add_rest_to_name=True)
    return name, unit


def best_str_to_name_unit(_str, default_unit=None):
    _str_copy = str(_str)
    unit_patterns = [
        ["[", "]"],
        ["(", ")"],
    ]
    name = str(_str).strip()
    unit = default_unit
    for pattern in unit_patterns:
        init, end = pattern
        if init in _str and end in _str:
            name, unit = str_to_name_unit_with_rest(_str, init=init, end=end, default_unit=None)
            break
    return name, unit


def create_vtk_header(dim: int, coord_dimensions: list):
    extent_str = ""
    for i in range(dim):
        extent_str += f"1 {coord_dimensions[i]} "
    if dim == 2:
        extent_str += "1 1 "
    extent_str = extent_str[:-1]

    header = rf"""<VTKFile type="RectilinearGrid" version="0.1" format="ascii">
<RectilinearGrid WholeExtent="{extent_str}">
<Piece Extent="{extent_str}">
    """

    return header
