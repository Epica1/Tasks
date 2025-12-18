import sys
import json
import argparse


class Assembler:
    OPCODES = {
        'load_const': 33,
        'read_mem': 19,
        'write_mem': 58,
        'abs': 26
    }

    def parse_high_level(self, source_content):
        intermediate = []

        for line_num, line in enumerate(source_content.strip().split('\n'), 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                if '=' in line:
                    left, right = line.split('=', 1)
                    left = left.strip()
                    right = right.strip()

                    # 1.Загрузка константы
                    if right.isdigit():
                        match = self._parse_reg(left)
                        if match:
                            dest_addr = match
                            const = int(right)
                            if const < 0 or const >= 2 ** 28:
                                raise ValueError(f"Константа {const} вне диапазона (0-2^28-1)")
                            intermediate.append({
                                'opcode': self.OPCODES['load_const'],
                                'dest_addr': dest_addr,
                                'const': const,
                                'type': 'load_const'
                            })
                            continue

                    # 2. Чтение из памяти
                    if right.startswith('MEM[') and right.endswith(']'):
                        inner = right[4:-1].strip()
                        if '+' in inner:
                            base_part, offset_part = inner.split('+', 1)
                            base_part = base_part.strip()
                            offset_part = offset_part.strip()

                            base_match = self._parse_reg(base_part)
                            if base_match and offset_part.isdigit():
                                dest_match = self._parse_reg(left)
                                if dest_match:
                                    intermediate.append({
                                        'opcode': self.OPCODES['read_mem'],
                                        'dest_addr': dest_match,
                                        'base_addr': base_match,
                                        'offset': int(offset_part),
                                        'type': 'read_mem'
                                    })
                                    continue

                    # 3. Запись в память
                    if left.startswith('MEM[') and left.endswith(']'):
                        mem_addr_str = left[4:-1].strip()
                        if mem_addr_str.isdigit():
                            src_match = self._parse_reg(right)
                            if src_match:
                                mem_addr = int(mem_addr_str)
                                if mem_addr < 0 or mem_addr >= 2 ** 24:
                                    raise ValueError(f"Адрес памяти {mem_addr} вне диапазона")
                                intermediate.append({
                                    'opcode': self.OPCODES['write_mem'],
                                    'mem_addr': mem_addr,
                                    'src_addr': src_match,
                                    'type': 'write_mem'
                                })
                                continue

                    # 4. ABS
                    if right.startswith('abs(MEM[') and right.endswith('])'):
                        inner = right[8:-2].strip()
                        base_match = self._parse_reg(inner)
                        if base_match:
                            dest_match = self._parse_reg(left)
                            if dest_match:
                                intermediate.append({
                                    'opcode': self.OPCODES['abs'],
                                    'dest_addr': dest_match,
                                    'base_addr': base_match,
                                    'type': 'abs'
                                })
                                continue

                raise ValueError(f"Неизвестный формат команды: {line}")

            except ValueError as e:
                print(f"Ошибка в строке {line_num}: {e}")
                sys.exit(1)

        return intermediate

    def _parse_reg(self, reg_str):
        reg_str = reg_str.strip()
        if reg_str.startswith('REG[') and reg_str.endswith(']'):
            addr_str = reg_str[4:-1].strip()
            if addr_str.isdigit():
                addr = int(addr_str)
                if 0 <= addr < 2 ** 6:
                    return addr
        return None

    @staticmethod
    def format_instruction(instr):
        if instr['type'] == 'load_const':
            return f"A={instr['opcode']}, B={instr['const']}, C={instr['dest_addr']}"
        elif instr['type'] == 'read_mem':
            return f"A={instr['opcode']}, B={instr['dest_addr']}, C={instr['base_addr']}, D={instr['offset']}"
        elif instr['type'] == 'write_mem':
            return f"A={instr['opcode']}, B={instr['mem_addr']}, C={instr['src_addr']}"
        elif instr['type'] == 'abs':
            return f"A={instr['opcode']}, B={instr['dest_addr']}, C={instr['base_addr']}"
        return str(instr)

    def encode_instruction(self, instr):
        if instr['type'] == 'load_const':
            a = instr['opcode'] & 0x3F
            b = instr['const'] & 0xFFFFFFF
            c = instr['dest_addr'] & 0x3F

            value = (c << 34) | (b << 6) | a

            bytes_list = []
            for i in range(5):
                bytes_list.append((value >> (i * 8)) & 0xFF)
            return bytes_list

        elif instr['type'] == 'read_mem':
            a = instr['opcode'] & 0x3F
            b = instr['dest_addr'] & 0x3F
            c = instr['base_addr'] & 0x3F
            d = instr['offset'] & 0x3FFF

            value = (d << 18) | (c << 12) | (b << 6) | a

            bytes_list = []
            for i in range(4):
                bytes_list.append((value >> (i * 8)) & 0xFF)
            return bytes_list

        elif instr['type'] == 'write_mem':
            a = instr['opcode'] & 0x3F
            b = instr['mem_addr'] & 0xFFFFFF
            c = instr['src_addr'] & 0x3F

            value = (c << 30) | (b << 6) | a

            bytes_list = []
            for i in range(5):
                bytes_list.append((value >> (i * 8)) & 0xFF)
            return bytes_list

        elif instr['type'] == 'abs':
            a = instr['opcode'] & 0x3F  # 6 бит
            b = instr['dest_addr'] & 0x3F  # 6 бит
            c = instr['base_addr'] & 0x3F  # 6 бит

            value = (c << 12) | (b << 6) | a

            bytes_list = []
            for i in range(3):
                bytes_list.append((value >> (i * 8)) & 0xFF)
            return bytes_list

        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    parser.add_argument('--test', action='store_true')

    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            source_content = f.read()

        assembler = Assembler()
        intermediate = assembler.parse_high_level(source_content)

        if args.test:
            print("Внутреннее представление программы:")
            print("=" * 50)
            for i, instr in enumerate(intermediate):
                print(f"Команда {i}: {assembler.format_instruction(instr)}")

                bytes_repr = assembler.encode_instruction(instr)
                hex_bytes = [f"0x{b:02X}" for b in bytes_repr]
                print(f"Байтовое представление: ({', '.join(hex_bytes)})")
                print()
            print("=" * 50)
            print(f"Всего команд: {len(intermediate)}")
        else:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                json.dump(intermediate, f, indent=2)
            print(f"Промежуточное представление сохранено в {args.output_file}")
            print(f"Всего команд: {len(intermediate)}")

    except FileNotFoundError:
        print(f"Ошибка: файл {args.input_file} не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

#python Config3_1.py program3.txt output.bin --test