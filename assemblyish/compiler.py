"""
MIT License

Copyright (c) 2021 vcokltfre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import List

from .parser import Token
from .errors import CompilationError
from .instruction import GOTO, VAR, instructions


class Compilable:
    def __init__(self, byte: int, line: int, index: int, args: List[Token], resolved_vars: dict = {}, resolved_gotos: dict = {}):
        """Represents a compilable line.

        Args:
            byte (int): The bytecode byte of the instruction associated.
        """

        self.byte = byte
        self.args = args

        self.line = line
        self.index = index

        self.vars = resolved_vars
        self.gotos = resolved_gotos

    def compile(self):
        compiled_bytes = [self.byte]

        is_goto = self.byte == 0b11111001

        for arg in self.args:
            if arg.type == "STR":
                compiled_bytes.extend(self.compile_string(arg.value))
            if arg.type == "IDT":
                if is_goto:
                    compiled_bytes.extend(self.make_bytes(self.gotos[arg.value], 8))
                    is_goto = False
                    continue
                compiled_bytes.extend(self.make_bytes(self.vars[arg.value], 8))
            if arg.type == "NUM":
                num = int(arg.value)
                compiled_bytes.extend(self.compile_int(num))

        print(compiled_bytes)

        return compiled_bytes

    def compile_string(self, string: str):
        string_bytes = [0b11111101]

        for letter in string:
            if ord(letter) > 255:
                raise CompilationError(self.line, self.index, f"Invalid character: {ord(letter)}")

        length = len(string)

        if length > 2**32:
            raise CompilationError(self.line, self.index, f"String too long. ({length} > {2**32})")

        string_bytes.extend(self.make_bytes(length, 4))

        string_bytes.extend([ord(c) for c in string])

        return string_bytes

    def compile_int(self, integer: int):
        int_bytes = [0b11111110]

        if integer > 2**64:
            raise CompilationError(self.line, self.index, f"Integer too large. ({integer} > {2**64})")

        int_bytes.extend(self.make_bytes(integer, 8))

        return int_bytes

    @staticmethod
    def make_bytes(num: int, length: int):
        bs = hex(num)[2:].zfill(length * 2)

        out = []

        for i in range(length):
            out.append(int(bs[i*2:i*2+2], 16))

        return out


class Compiler:
    def __init__(self, filename: str, tokens: List[Token]):
        """A compiler class for assemblyish.

        Args:
            filename (str): The filename of the file being compiled. Used for error logging.
            tokens (List[Token]): A list of Token objects representing the program's code.
        """

        self.filename = filename
        self.tokens = tokens

        self.variables = {}
        self.gotos = {}

        self.var_goto_id = 1

        self.instrs = []

        self.lines = self.getlines()

    def compile(self):
        for line in self.lines:
            if line[0].type == "IDT":
                instruction = instructions.get(line[0].value)

                if not instruction:
                    raise CompilationError(line[0].line, line[0].index, f"Not a valid instruction: {line[0].value}.")

                if not instruction.match(line[1:]):
                    raise CompilationError(line[1].line, line[1].index, f"Argument signature doesn't match.")

                for token in line[1:]:
                    if line[0].value != "GOTO":
                        if token.type == "IDT" and token.value not in self.variables:
                            raise CompilationError(line[1].line, line[1].index, f"Variable referenced before definition.")
                    else:
                        if token.type == "IDT" and token.value not in self.gotos:
                            raise CompilationError(line[1].line, line[1].index, f"Goto referenced before definition.")

                self.instrs.append(Compilable(instruction.byte, line[0].line, line[0].index, line[1:], self.variables, self.gotos))
            elif line[0].type == "VAR":
                if not VAR.match(line[1:]):
                    raise CompilationError(line[1].line, line[1].index, f"Variable definition does not match correct signature.")
                self.variables[line[1].value] = id = self.var_goto_id
                self.var_goto_id += 1
                self.instrs.append(Compilable(VAR.byte, line[0].line, line[0].index, [Token("NUM", 0, 0, id)]))
            elif line[0].type == "GOTO":
                if not GOTO.match(line[1:]):
                    raise CompilationError(line[1].line, line[1].index, f"Goto definition does not match correct signature.")
                self.gotos[line[1].value] = id = self.var_goto_id
                self.var_goto_id += 1
                self.instrs.append(Compilable(GOTO.byte, line[0].line, line[0].index, [Token("NUM", 0, 0, id)]))
            else:
                raise CompilationError(line[0].line, line[0].index, f"Lines must start with an identifier, variable declaration (.), or goto (:).")

        code = []

        for c in self.instrs:
            code.extend(c.compile())

        return code

    def save(self, filename: str):
        with open(filename, "wb") as f:
            self.save_to_file(f)

    def save_to_file(self, writable):
        writable.write(bytes(self.compile()))

    def getlines(self) -> List[List[Token]]:
        lines = []
        line = []

        for token in self.tokens:
            if token.type == "NEWLINE":
                if line:
                    lines.append(line)
                    line = []
            else:
                line.append(token)

        if line:
            lines.append(line)

        return lines
