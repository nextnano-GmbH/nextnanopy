from nextnanopy.utils.mycollections import DictList
from nextnanopy.inputs import InputFileTemplate
from nextnanopy.nnp.defaults import (
    parse_nnp_variable,
    is_nnp_variable,
    InputVariable_nnp,
)
from nextnanopy.negf.defaults import is_negf_input_text
from nextnanopy.utils.misc import savetxt


class InputFile(InputFileTemplate):
    def load_variables(self):
        variables = DictList()
        for i, line in enumerate(self.raw_lines):
            if not is_nnp_variable(line):
                continue
            name, value, comment = parse_nnp_variable(line)
            var = InputVariable_nnp(
                name=name, value=value, comment=comment, metadata={"line_idx": i}
            )
            variables[var.name] = var
        self.variables = variables
        return self.variables

    def save(self, fullpath=None, overwrite=False, automkdir=True, content=False):
        if fullpath is None:
            if self.fullpath is None:
                raise ValueError("Please specify a fullpath")
            fullpath = self.fullpath
        if content:
            text = self.content.__str__()
        else:
            text = self.text
        self.fullpath = savetxt(
            fullpath=fullpath, text=text, overwrite=overwrite, automkdir=automkdir
        )
        return self.fullpath

    def validate(self):
        if not is_negf_input_text(self.raw_text):
            raise ValueError(f"Not a valid nextnano.NEGF++ input file")
