from nextnanopy.utils.mycollections import DictList
from nextnanopy.inputs import InputFileTemplate
from nextnanopy.negf.defaults import (
    is_negf_classic_input_text,
    InputVariable_NEGF,
    parse_negf_variable_name,
)
from nextnanopy.utils.formatting import autofmt_variable_value
import xml.etree.ElementTree as ET


class InputFile(InputFileTemplate):
    def load_variables(self):
        # parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)) #Does not supported in python3.7
        parser = ET.XMLParser()
        root = ET.fromstring(self.text, parser=parser)
        varsection = root.find("Variables")
        variables = DictList()
        if not varsection:
            self.variables = variables
            return self.variables
        vars = varsection.findall("Constant")

        for var in vars:
            name_element = var.find("Name")
            name = parse_negf_variable_name(name_element.text)
            comment = name_element.get("Comment")
            value_element = var.find("Value")
            value = autofmt_variable_value(value_element.text)
            unit = value_element.get("Unit")
            var = InputVariable_NEGF(name=name, value=value, unit=unit, comment=comment)
            variables[name] = var
        self.variables = variables
        return self.variables

    @property
    def lines(self):
        root = ET.fromstring(self.raw_text)
        varsection = root.find("Variables")
        variables = self.variables
        if varsection:
            vars = varsection.findall("Constant")
            for var_element in vars:
                for variable in variables:
                    name_element = var_element.find("Name")
                    if name_element.text == "$" + variable.name:
                        value_element = var_element.find("Value")
                        value_element.text = str(variable.value)
                        name_element.set("Comment", variable.comment)
                        value_element.set("Unit", variable.unit)

        xmlstr = ET.tostring(root, encoding="unicode", method="xml")
        lines_result = xmlstr.splitlines()
        return lines_result

    def validate(self):
        if not is_negf_classic_input_text(self.raw_text):
            raise ValueError(f"Not valid nextnano.NEGF input file")
