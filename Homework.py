import sys
import re
import argparse
from typing import Dict, Any, Union

Value = Union[int, float, str, Dict[str, Any], bool]


class ConfigParser:
    def __init__(self):
        self.constants: Dict[str, Value] = {}

    def tokenize(self, text: str):
        patterns = [
            (r'\d+(?:\.\d*)?|\.\d+', 'NUMBER'),
            (r'"[^"]*"', 'STRING'),
            (r'\{', 'LBRACE'),
            (r'\}', 'RBRACE'),
            (r'->', 'ARROW'),
            (r'<-', 'ASSIGN'),
            (r'\[', 'LBRACKET'),
            (r'\]', 'RBRACKET'),
            (r'\.', 'DOT'),
            (r';', 'SEMICOLON'),
            (r'true|false', 'BOOLEAN'),
            (r'[_a-zA-Z]+', 'IDENT'),
            (r'#.*', 'COMMENT'),
            (r'\s+', 'SPACE'),
        ]

        tokens = []
        pos = 0

        while pos < len(text):
            match = None
            for pattern, tag in patterns:
                regex = re.compile(pattern)
                match = regex.match(text, pos)
                if match:
                    if tag != 'SPACE' and tag != 'COMMENT':
                        tokens.append((tag, match.group()))
                    pos = match.end()
                    break
            if not match:
                raise SyntaxError(f"Unexpected char at {pos}: {text[pos]}")

        return tokens

    def parse(self, text: str) -> Dict[str, Any]:
        tokens = self.tokenize(text)
        self.pos = 0

        def peek():
            return tokens[self.pos] if self.pos < len(tokens) else None

        def consume(tag=None):
            token = tokens[self.pos]
            self.pos += 1
            if tag and token[0] != tag:
                raise SyntaxError(f"Expected {tag}, got {token[0]}")
            return token

        def parse_value():
            token = peek()
            if not token:
                return None

            if token[0] == 'NUMBER':
                consume('NUMBER')
                return float(token[1]) if '.' in token[1] else int(token[1])
            elif token[0] == 'STRING':
                consume('STRING')
                return token[1][1:-1]
            elif token[0] == 'BOOLEAN':
                consume('BOOLEAN')
                return token[1] == 'true'
            elif token[0] == 'LBRACKET':
                consume('LBRACKET')
                const_name = consume('IDENT')[1]
                consume('RBRACKET')
                if const_name not in self.constants:
                    raise NameError(f"Undefined constant: {const_name}")
                return self.constants[const_name]
            elif token[0] == 'LBRACE':
                return parse_dict()
            elif token[0] == 'IDENT':
                const_name = token[1]
                if const_name in self.constants:
                    consume('IDENT')
                    return self.constants[const_name]
                else:
                    raise SyntaxError(f"Unexpected identifier: {const_name}")
            else:
                raise SyntaxError(f"Unexpected token: {token}")

        def parse_dict():
            consume('LBRACE')
            result = {}

            while peek() and peek()[0] != 'RBRACE':
                key = consume('IDENT')[1]
                consume('ARROW')
                value = parse_value()
                result[key] = value
                consume('DOT')

            consume('RBRACE')
            return result

        while self.pos < len(tokens):
            if peek()[0] == 'IDENT' and self.pos + 1 < len(tokens) and tokens[self.pos + 1][0] == 'ASSIGN':
                name = consume('IDENT')[1]
                consume('ASSIGN')
                value = parse_value()
                self.constants[name] = value
                consume('SEMICOLON')
            else:
                break

        return parse_dict() if self.pos < len(tokens) else {}

    def to_toml(self, data: Dict[str, Any], prefix: str = "") -> str:
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                new_prefix = f"{prefix}.{key}" if prefix else key
                lines.append(f"\n[{new_prefix}]")
                lines.append(self.to_toml(value, new_prefix))
            elif isinstance(value, str):
                escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                lines.append(f'{key} = "{escaped}"')
            elif isinstance(value, bool):
                lines.append(f'{key} = {str(value).lower()}')
            else:
                lines.append(f'{key} = {value}')
        return '\n'.join(lines).strip()


def main():
    parser = argparse.ArgumentParser(
        description='Convert configuration language to TOML',
        usage='python config_parser.py <input_file>'
    )
    parser.add_argument(
        'input_file',
        help='Path to input configuration file'
    )

    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        config_parser = ConfigParser()
        data = config_parser.parse(text)
        toml_output = config_parser.to_toml(data)

        print(toml_output)

    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        sys.exit(1)
    except NameError as e:
        print(f"Name error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

#python .\Homework.py .\Homework.conf