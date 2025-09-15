from nextnanopy.utils.mycollections import DictList
from nextnanopy.inputs import InputFileTemplate
from nextnanopy.nnp.defaults import parse_nnp_variable, is_nnp_input_text, is_nnp_variable, InputVariable_nnp
from nextnanopy.utils.misc import savetxt
import os

class InputFile(InputFileTemplate):
    def load_variables(self):
        variables = DictList()
        for i, line in enumerate(self.raw_lines):
            if not is_nnp_variable(line):
                continue
            name, value, comment = parse_nnp_variable(line)
            var = InputVariable_nnp(name=name, value=value, comment=comment, metadata={'line_idx': i})
            variables[var.name] = var
        self.variables = variables
        return self.variables

    def load_content(self):
        parser = Parser()
        #parser.parse(self.raw_lines, mode='lines')
        #print(self.raw_lines)
        parser.parse(self.lines, mode = 'lines')
        # result = parser.result
        # return result
        self.content = parser.result
    # @property
    # def content(self):
    #     return self.load_content()

    def save(self, fullpath=None, overwrite=False, automkdir=True, content = False, temp=False):
        """
        content=True invokes the demo feature of saving self.content instead of self.test

        be aware that the content=True ignores comments
        """
        if fullpath is None:
            if temp:
                folder = self._get_temp_dir()
                fullpath = os.path.join(folder, self.filename)
            elif self.fullpath is None:
                raise ValueError('Please, specify a fullpath')
            else:
                fullpath = self.fullpath
        if content:
            text = self.content.__str__()
        else:
            text = self.text
        self.fullpath = savetxt(fullpath=fullpath, text=text, overwrite=overwrite, automkdir=automkdir)
        return self.fullpath



    def validate(self):
        if not is_nnp_input_text(self.raw_text):
            raise ValueError(f'Not a valid nextnano++ input file')



######### objects to create abstract object of

def content_to_lines(content_to_transform):
    if isinstance(content_to_transform, str):
        return content_to_transform.split(sep='\n')
    else:
        result = []
        for c in content_to_transform:
            result.extend(c.__str__().split(sep='\n'))
        return result


class Comment(object): #just to be able to check that entry is comment
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        self.text.__repr__()

    def __str__(self):
        self.text.__str__()


class Entry(object):
    def __init__(self, content, intend_sign = '    '):
        self.content = content
        self.intend_sign = intend_sign

    @property
    def lines(self, intend_level = 0):
        if isinstance(self.content, str):
            text_lines = content_to_lines(self.content)
        else:
            text_lines = []
            for c in self.content:
                text_lines.extend(content_to_lines(c.__str__()))
        for i, _ in enumerate(text_lines):
            text_lines[i] = intend_level * self.intend_sign + text_lines[i]

        return text_lines



    def __repr__(self):
        result = ''
        for line in self.lines:
            result += line + '\n'
        return result

    @property
    def dict_representation(self):
        result = DictList()
        for i, entry in enumerate(self.content):
            if isinstance(entry, Block):
                result[entry.name] = entry
            else:
                result[f'_entry_{i}'] = entry
        return result

    def __getitem__(self, item):
        return self.dict_representation[item]

    def __setitem__(self, item, val):

        self.dict_representation[item] = val
        if isinstance(item, int):
            self.content[item] = val
        else:
            i = self.dict_representation.get_indx(item)
            self.content[i] = val

    def __delitem__(self, item):
        del self.dict_representation[item]
        if isinstance(item, int):
            del self.content[item]
        else:
            i = self.dict_representation.get_indx(item)
            del self.content[i]





class Block(Entry):
    def __init__(self, name, content, parent_block = None, intend_sign = '    '):
        self.content = content
        self.intend_sign = intend_sign
        self.name = name
        self.parent_block = parent_block

    @property
    def lines(self, intend_level=1):
        if isinstance(self.content, str):
            text_lines = content_to_lines(self.content)
        else:
            text_lines = []
            for c in self.content:
                text_lines.extend(content_to_lines(c.__str__()))
        for i, _ in enumerate(text_lines):
            text_lines[i] = intend_level * self.intend_sign + text_lines[i]

        text_lines.insert(0, self.name + '{')
        if self.content:
            text_lines.append('}')
        else:
            text_lines[-1]+='}'

        return text_lines



class Parser(object):
    def __init__(self):
        self.lines = []
        self.result = Entry([])

    def parse(self, input, mode = 'str'):
        if mode == 'str':
            self.lines = input.split(sep = '\n')
        elif mode == 'lines':
            self.lines = input
        self.delete_comments()
        self.replace_brackets()
        last_word = ''
        current_block = self.result
        level = 0
        for line in self.lines:
            words_in_line = line.split()
            content_line = ''
            for word in words_in_line:
                if word == '{':
                    level+=1
                    name_of_the_block = last_word
                    new_block = Block(name_of_the_block, [])
                    if content_line:
                        content_line_without_last_word = content_line.rsplit(' ', 1) #split to beginning and last word

                        if not content_line_without_last_word[1]:
                            content_line = '' #if only one word was in content_line - it is name of the block, so delete it from content line
                        else:
                            content_line = content_line_without_last_word[0]
                            current_block.content.append(content_line)
                    current_block.content.append(new_block)
                    new_block.parent_block  = current_block
                    current_block = new_block
                    content_line = ''

                elif word == '}':
                    if level<1:
                        raise ValueError('Incorrect string to parse. } closed before opening')
                    level = level -1
                    if content_line:
                        current_block.content.append(content_line)
                    current_block = current_block.parent_block
                    last_word = ''

                else:
                    content_line += word+' '
                    last_word = word
            if content_line:
                current_block.content.append(content_line)
        if level != 0:
            raise ValueError('Incorrect string to parse. { not closed')



    def clear(self):
        self.lines = []
        self.result = Entry([])




    def delete_comments(self):
        for i, _ in enumerate(self.lines):
            if self.lines[i].startswith('#'):
                self.lines[i] = ''
            else:
                self.lines[i] = self.lines[i].split(sep = '#')[0]

    def replace_brackets(self):
        for i, _ in enumerate(self.lines):
            self.lines[i] = self.lines[i].replace('{', ' { ')
            self.lines[i] = self.lines[i].replace('}', ' } ')
            self.lines[i] = self.lines[i].replace('[', ' [ ')
            self.lines[i] = self.lines[i].replace(']', ' ] ')
            self.lines[i] = self.lines[i].replace('(', ' ( ')


    def text(self):
        result = ''
        for line in self.lines:
            result += line + '\n'
        return result