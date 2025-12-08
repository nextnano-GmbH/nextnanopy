from nextnanopy.nnp.inputs import InputFile as InputFileTemplateNnp
from nextnanopy.msb.defaults import is_msb_input_text


class InputFile(InputFileTemplateNnp): # inherits from NNP InputFile
    def validate(self):
        if not is_msb_input_text(self.raw_text):
            raise ValueError(f'Not valid nextnano.MSB input file')
