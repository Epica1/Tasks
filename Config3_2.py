import sys
import argparse
import struct


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

                    # 1. Загрузка константы
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

    def assemble_to_binary(self, intermediate):
        binary_data = bytearray()

        for instr in intermediate:
            opcode = instr['opcode']

            if instr['type'] == 'load_const':
                const = instr['const']
                dest_addr = instr['dest_addr']
                value = (dest_addr << 34) | (const << 6) | opcode
                binary_data.extend(struct.pack('<Q', value)[:5])

            elif instr['type'] == 'read_mem':
                dest_addr = instr['dest_addr']
                base_addr = instr['base_addr']
                offset = instr['offset']
                value = (offset << 18) | (base_addr << 12) | (dest_addr << 6) | opcode
                binary_data.extend(struct.pack('<I', value)[:4])

            elif instr['type'] == 'write_mem':
                mem_addr = instr['mem_addr']
                src_addr = instr['src_addr']
                value = (src_addr << 30) | (mem_addr << 6) | opcode
                binary_data.extend(struct.pack('<Q', value)[:5])

            elif instr['type'] == 'abs':
                dest_addr = instr['dest_addr']
                base_addr = instr['base_addr']
                value = (base_addr << 12) | (dest_addr << 6) | opcode
                binary_data.extend(struct.pack('<I', value)[:3])

        return bytes(binary_data)

    @staticmethod
    def format_instruction(instr):
        opcode = instr['opcode']

        if instr['type'] == 'load_const':
            const = instr['const']
            dest_addr = instr['dest_addr']
            value = (dest_addr << 34) | (const << 6) | opcode
            bytes_hex = ', '.join(f'0x{b:02X}' for b in struct.pack('<Q', value)[:5])
            return f"A: {opcode}, B: {const}, C: {dest_addr} -> {bytes_hex}"

        elif instr['type'] == 'read_mem':
            dest_addr = instr['dest_addr']
            base_addr = instr['base_addr']
            offset = instr['offset']
            value = (offset << 18) | (base_addr << 12) | (dest_addr << 6) | opcode
            bytes_hex = ', '.join(f'0x{b:02X}' for b in struct.pack('<I', value)[:4])
            return f"A: {opcode}, B: {dest_addr}, C: {base_addr}, D: {offset} -> {bytes_hex}"

        elif instr['type'] == 'write_mem':
            mem_addr = instr['mem_addr']
            src_addr = instr['src_addr']
            value = (src_addr << 30) | (mem_addr << 6) | opcode
            bytes_hex = ', '.join(f'0x{b:02X}' for b in struct.pack('<Q', value)[:5])
            return f"A: {opcode}, B: {mem_addr}, C: {src_addr} -> {bytes_hex}"

        elif instr['type'] == 'abs':
            dest_addr = instr['dest_addr']
            base_addr = instr['base_addr']
            value = (base_addr << 12) | (dest_addr << 6) | opcode
            bytes_hex = ', '.join(f'0x{b:02X}' for b in struct.pack('<I', value)[:3])
            return f"A: {opcode}, B: {dest_addr}, C: {base_addr} -> {bytes_hex}"

        return str(instr)


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
        binary_code = assembler.assemble_to_binary(intermediate)
        num_commands = len(intermediate)

        if args.test:
            print("Результат ассемблирования:")
            print("=" * 50)
            for i, instr in enumerate(intermediate):
                print(f"Инструкция {i}: {assembler.format_instruction(instr)}")
            print("=" * 50)
            print(f"Число ассемблированных команд: {num_commands}")
        else:
            with open(args.output_file, 'wb') as f:
                f.write(binary_code)
            print(f"Бинарный код сохранен в {args.output_file}")
            print(f"Размер файла: {len(binary_code)} байт")
            print(f"Число ассемблированных команд: {num_commands}")

    except FileNotFoundError:
        print(f"Ошибка: файл {args.input_file} не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

#python Config3_2.py program.txt output.bin --test
#python Config3_2.py program.txt output.bin