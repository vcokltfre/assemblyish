
from typing import List

from .parser import Token


class Argument:
    def __init__(self, *types: List[str], required: bool = True):
        self.types = types
        self.required = required

    def match(self, thing):
        return thing.type in self.types


class Instruction:
    def __init__(self, byte: int, *args: List[Argument]):
        """An instruction in assemblyish.

        Args:
            byte (int): The instruction's bytecode byte.
        """

        self.byte = byte
        self.args = args

    def match(self, line: List[Token]):
        if len(line) > len(self.args):
            return False
        for i, arg in enumerate(self.args):
            if i == len(line):
                if not arg.required:
                    return True
                else:
                    return False
            if not arg.match(line[i]):
                return False
        return True


instructions = {
    "ADD":  Instruction(1, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),
    "SUB":  Instruction(2, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),
    "MUL":  Instruction(3, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),
    "DIV":  Instruction(4, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),
    "POW":  Instruction(5, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),
    "MOD":  Instruction(6, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),
    "RAN":  Instruction(7, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),

    "STO":  Instruction(65, Argument("IDT"), Argument("NUM", "STR", "IDT", required=False)),
    "LOD":  Instruction(66, Argument("IDT"), Argument("NUM", "STR", "IDT", required=False)),

    "OUT":  Instruction(129, Argument("NUM", "IDT", required=False)),
    "OUTS": Instruction(130, Argument("STR", "IDT", required=False)),
}

GOTO = Instruction(0b11111001, Argument("IDT"))
VAR = Instruction(0b11111010, Argument("IDT"))
