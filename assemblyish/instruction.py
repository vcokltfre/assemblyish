
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
    "ADD": Instruction(0b00000001, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),
    "SUB": Instruction(0b00000010, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),
    "MUL": Instruction(0b00000011, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),
    "DIV": Instruction(0b00000100, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),
    "POW": Instruction(0b00000101, Argument("NUM", "IDT"), Argument("NUM", "IDT", required=False)),

    "STO": Instruction(0b00000101, Argument("IDT"), Argument("NUM", "STR", "IDT", required=False)),

    "OUT": Instruction(0b01000001, Argument("NUM", "IDT", required=False)),
    "OUTS": Instruction(0b01000001, Argument("STR", "IDT", required=False)),
}

GOTO = Instruction(0b11111001, Argument("IDT"))
VAR = Instruction(0b11111010, Argument("IDT"))
