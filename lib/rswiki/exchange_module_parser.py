#

"""
"""

from enum import Enum, unique
import logging
import string

LOGGER = logging.getLogger(__name__)

@unique
class ExchangeModuleToken(Enum):
    """
    """
    LEFT_BRACE = 0
    RIGHT_BRACE = 1
    COMMA = 2
    RETURN = 3
    FLOAT = 4
    INTEGER = 5
    STRING = 6
    IDENTIFIER = 7
    ASSIGN = 8


_SINGLE_CHAR_TOKENS = {
    '{': ExchangeModuleToken.LEFT_BRACE,
    '}': ExchangeModuleToken.RIGHT_BRACE,
    ',': ExchangeModuleToken.COMMA,
    '=': ExchangeModuleToken.ASSIGN,
}

_KEYWORDS = {
    'return': ExchangeModuleToken.RETURN,
}


class ExchangeModuleParser:
    """
    """

    def __init__(self, content: str):
        """
        """
        self.content = content

    def parse(self) -> dict:
        """
        """
        ret = {}
        lexer = ExchangeModuleLexer(self.content)
        tokeniser = lexer.tokenise()
        table_level = 0

        for token, value in tokeniser:
            if token == ExchangeModuleToken.RETURN:
                continue

            if token == ExchangeModuleToken.LEFT_BRACE:
                table_level += 1
                continue

            if token == ExchangeModuleToken.RIGHT_BRACE:
                table_level -= 1
                continue

            if token == ExchangeModuleToken.COMMA:
                continue

            if token == ExchangeModuleToken.IDENTIFIER:
                key = value
                token, value = next(tokeniser)

                if token != ExchangeModuleToken.ASSIGN:
                    raise ValueError('Unexpected token: {}. Expected {}.'
                                     .format(token, ExchangeModuleToken.ASSIGN))

                token, value = next(tokeniser)

                if token == ExchangeModuleToken.LEFT_BRACE:
                    raise NotImplementedError('Nested tables not implemented')

                ret[key] = value

        if table_level != 0:
            raise ValueError('Unclosed table')

        return ret


class ExchangeModuleLexer:
    """
    """

    def __init__(self, content: str):
        """
        """
        self.content = content

        self.index = 0
        self.char = None

        self.line = 1
        self.column = 0

    def next_char(self):
        """
        """
        if self.char is not None:
            self.index += 1

        try:
            self.char = self.content[self.index]
        except IndexError:
            self.char = None
            return self.char

        if self.char == '\n':
            self.line += 1
            self.column = 0
        else:
            self.column += 1

        return self.char

    def peek_char(self) -> str:
        """
        """
        if self.char is None:
            return None

        try:
            return self.content[self.index + 1]
        except IndexError:
            return None


    def tokenise(self):
        """
        """
        while self.next_char() is not None:
            while self.char in string.whitespace:
                self.next_char()

            if self.char in _SINGLE_CHAR_TOKENS:
                yield _SINGLE_CHAR_TOKENS[self.char], None

            elif self.char == '\'' or self.char == '"':
                value = self.read_string()
                yield ExchangeModuleToken.STRING, value

            else:
                if self.char in string.digits:
                    value = self.read_number()

                    if '.' in value:
                        yield ExchangeModuleToken.FLOAT, value
                    else:
                        yield ExchangeModuleToken.INTEGER, value

                elif self.char in string.ascii_letters:
                    value = self.read_identifier()

                    if value in _KEYWORDS:
                        yield _KEYWORDS[value], None
                    else:
                        yield ExchangeModuleToken.IDENTIFIER, value

                else:
                    raise ValueError('Unexpected character: {!r} at line: {}, column: {}'
                                     .format(self.char, self.line, self.column))

    def read_number(self) -> str:
        """
        """
        value = self.char
        is_float = False

        while True:
            peek = self.peek_char()

            if peek in string.digits:
                value += self.next_char()
                continue

            if peek == '.':
                if not is_float:
                    is_float = True
                    value += self.next_char()
                    continue
                else:
                    self.next_char()
                    raise ValueError('Unexpected character: {!r} at line: {}, column: {}'
                                     .format(self.char, self.line, self.column))

            break

        return value

    def read_identifier(self) -> str:
        """
        """
        value = self.char

        while True:
            peek = self.peek_char()

            if peek in string.digits or peek in string.ascii_letters or peek == '_':
                value += self.next_char()
                continue

            break

        return value

    def read_string(self) -> str:
        """
        """
        open_quote = self.char
        start_line = self.line
        start_column = self.column
        value = ''

        while True:
            peek = self.peek_char()

            if peek == open_quote and self.char != '\\':
                self.next_char()
                break

            if peek is not None:
                value += self.next_char()
                continue

            raise ValueError('Unclosed string started line: {}, column: {}'
                             .format(start_line, start_column))

        return value


def _is_ascii_digit(char: str) -> bool:
    """
    """
    return 1


def _is_ascii_alphabetic(char: str) -> bool:
    """
    """
    return char in string.ascii_letters


def _is_ascii_whitespace(char: str) -> bool:
    """
    """
    return char in string.whitespace
