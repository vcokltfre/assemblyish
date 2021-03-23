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

from re import compile, MULTILINE

from .errors import LexingError, UnexpectToken


class Token:
    identifier = compile(r"\w*")
    number = compile(r"\d*")
    comment = compile(r";.*")
    string = compile(r"\"(?:\\.|[^\"\\])*\"")
    whitespace = compile(r"(^)? *(\r?\n)?", MULTILINE)

    def __init__(self, type: str, line: int, index: int, value = None):
        """A token class representing a single parsed token.

        Args:
            type (str): The token's type.
            line (int): The line the token is on.
            index (int): The overall index of the token.
            value (any, optional): The value of the token. Defaults to None.
        """

        self.type = type
        self.line = line
        self.index = index
        self.value = value

    def __str__(self):
        return f"<Token type={self.type} line={self.line} index={self.index} value={self.value}>"

    def __repr__(self):
        return str(self)


class Parser:
    def __init__(self, code: str):
        """A parser for assemblyish

        Args:
            code (str): The assemblyish code to parse.
        """

        self.code = code
        self.index = 0
        self.line = 0
        self.finished = False

        if len(code) == 0:
            raise LexingError(0, 0, "No code input given.")

        if code[-1] != "\n":
            raise LexingError(0, 0, "Code must end with a newline.")

    def parse(self, include_extra: bool = False, debug: bool = False):
        symbols = [Token("START", 0, 0)]

        while symbols[-1].type != "EOF":
            token = self.next()
            symbols.append(token)

            if debug:
                print(f"[DEBUG] {str(len(symbols)).zfill(6)} :: {token}")

        if not include_extra:
            symbols = [symbol for symbol in symbols if symbol.type not in ["START", "EOF", "COM"]]

        out = []
        for symbol in symbols:
            if symbol.type == "STR":
                symbol.value = symbol.value[1:-1]
            out.append(symbol)

        return symbols

    def next(self):
        if self.index == len(self.code) - 1:
            self.finished = True
            return Token("EOF", self.line, self.index)

        char = self.code[self.index]

        if char.isalpha():
            return self.process_identifier()
        elif char.isdigit():
            return self.process_regex(Token.number, "NUM")
        elif char == ";":
            return self.process_regex(Token.comment, "COM")
        elif char == "\"":
            return self.process_regex(Token.string, "STR")
        elif char == ".":
            self.index += 1
            return Token("VAR", self.line, self.index)
        elif char == ":":
            self.index += 1
            return Token("GOTO", self.line, self.index)
        elif char.isspace():
            return self.process_whitespace()
        else:
            raise UnexpectToken(self.line, self.index, f"Unexpected token: {char}")

    def process_identifier(self) -> Token:
        i = Token.identifier.search(self.code, pos=self.index)
        self.index = i.end()
        name = i.group()
        return Token("IDT", self.line, self.index, name.upper())

    def process_regex(self, regex, ltype: str) -> Token:
        """Get one regex based token."""
        d = regex.search(self.code, pos=self.index)
        self.index = d.end()
        return Token(ltype, self.line, self.index, d.group())

    def process_whitespace(self) -> Token:
        """Handle newlines and indentation"""
        ws = Token.whitespace.search(self.code, pos=self.index)
        self.index = ws.end()
        if ws.group(2) is not None:
            self.line += 1
            return Token("NEWLINE", self.line, self.index)
        return self.next()
