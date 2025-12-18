'''import os  # модуль os для взаимодействия с операционной системой(получение имени пользователя)
import socket  # для работы с сетевыми соединениями (получение имени хоста)
import argparse  # модуль, который помогает обрабатывать аргументы, переданные из командной строки
import sys  # модуль для взаимодействия с системой (например завершение программы sys.exit)


def execute_script(script_path, prompt_base): # определяет функцию, которая принимает путь к скрипту и "базу приглашения", и выполняет команды из файла
    try:  # начало блока обработки, для нахождения ошибок, при открытии файла
        with open(script_path, 'r') as f:  # открывает файл скрипта в режиме чтения
            for line in f:
                line = line.strip()  # удаление лишних пробелов и переносов в начале и конце строки
                if not line:
                    continue

                print(f"{prompt_base} {line}")  # имитация вывода команд
                execute_command(line, prompt_base)  # выполнение команды из строки
    except FileNotFoundError: # обработка исключений, если файл не найден
        print(f"Ошибка: скрипт {script_path} не найден")  # вывод сообщения об ошибке
    except Exception as e: # обработка других исключений
        print(f"Ошибка при выполнении скрипта: {e}") # вывод сообщения об ошибке


def execute_command(user_input, prompt_base): # функция принимает ввод пользователя
    parts = user_input.split()  # разбивает введенную строку на список слов по пробелу
    command = parts[0]  # первое слово является командой
    args = parts[1:]  # остальное аргументы

    if command == "exit":
        print("Выход из эмулятора...")
        sys.exit(0)

    elif command == "ls":
        print(f"Команда: ls, аргументы: {args}")

    elif command == "cd":
        print(f"Команда: cd, аргументы: {args}")

    elif command == "conf-dump":
        print("Параметры эмулятора:")  # заголовок вывода конфигурации
        print(f"  VFS путь: {config.vfs_path}")  # вывод пути к VFS
        print(f"  Скрипт: {config.script_path}")  # вывод пути к скрипту

    else:
        print(f"Ошибка: неизвестная команда '{command}'")  # вывод сообщения об ошибке


def main():
    parser = argparse.ArgumentParser(description='Эмулятор командной строки UNIX')  # создание парсера аргументов
    parser.add_argument('--vfs', dest='vfs_path', default='./vfs',  # добавление аргумента --vfs
                        help='Путь к физическому расположению VFS')  # текст помощи для аргумента
    parser.add_argument('--script', dest='script_path',  # добавление аргумента --script
                        help='Путь к стартовому скрипту')  # текст помощи для аргумента
    global config  # объявление глобальной переменной config
    config = parser.parse_args()  # разбор аргументов командной строки и сохранение в config

    print("=== Параметры эмулятора ===")  # заголовок отладочного вывода
    print(f"VFS путь: {config.vfs_path}")  # вывод пути к VFS
    print(f"Скрипт: {config.script_path}")  # вывод пути к скрипту
    print("===========================")  # разделитель

    username = os.getlogin()  # возвращает имя текущего пользователя
    hostname = socket.gethostname()  # возвращает имя текущего хоста
    prompt_base = f"{username}@{hostname}:~$"

    print(f"Эмулятор командной строки UNIX")
    print(f"Для выхода введите 'exit'")
    print("-" * 40)

    if config.script_path:  # проверка, был ли указан путь к скрипту
        execute_script(config.script_path, prompt_base)  # вызов функции выполнения скрипта

    while True:  # бесконечный цикл для интерактивного режима
        user_input = input(prompt_base + " ").strip()  # получение ввода от пользователя с приглашением

        if not user_input:
            continue

        execute_command(user_input, prompt_base)  # функция выполнения команды


if __name__ == "__main__":  # проверка, что скрипт запущен напрямую
    main()
'''

import os
import socket
import argparse
import sys


class VFS:
    def __init__(self, vfs_path):
        self.vfs_path = os.path.abspath(vfs_path)
        self.current_dir = "/"

        # Создаем корневую директорию VFS если она не существует
        if not os.path.exists(self.vfs_path):
            os.makedirs(self.vfs_path)

    def get_real_path(self, vfs_path=None):
        """Преобразует VFS путь в реальный путь в файловой системе"""
        if vfs_path is None:
            vfs_path = self.current_dir

        # Нормализуем VFS путь
        if vfs_path.startswith("/"):
            abs_vfs_path = vfs_path
        else:
            abs_vfs_path = os.path.join(self.current_dir, vfs_path)

        # Убираем начальный слэш для корректного объединения
        abs_vfs_path = abs_vfs_path.lstrip("/")

        # Собираем реальный путь
        real_path = os.path.join(self.vfs_path, abs_vfs_path)

        return os.path.normpath(real_path)

    def ls(self, path=None):
        """Показывает содержимое директории в VFS"""
        real_path = self.get_real_path(path)

        if not os.path.exists(real_path):
            return f"ls: невозможно получить доступ к '{path}': Нет такого файла или директории"

        if not os.path.isdir(real_path):
            return f"ls: '{path}': Это не директория"

        try:
            items = os.listdir(real_path)
            # Разделяем файлы и директории для красивого вывода
            dirs = []
            files = []

            for item in items:
                item_path = os.path.join(real_path, item)
                if os.path.isdir(item_path):
                    dirs.append(item + "/")
                else:
                    files.append(item)

            result = []
            if dirs:
                result.extend(sorted(dirs))
            if files:
                result.extend(sorted(files))

            return "\n".join(result)
        except PermissionError:
            return f"ls: невозможно открыть директорию '{path}': Отказано в доступе"

    def cd(self, path):
        """Изменяет текущую директорию в VFS"""
        if not path:
            path = "/"

        # Специальный случай - переход в корень
        if path == "/":
            self.current_dir = "/"
            return None

        # Определяем целевой путь
        if path.startswith("/"):
            # Абсолютный путь
            target_dir = path
        else:
            # Относительный путь
            if self.current_dir == "/":
                target_dir = "/" + path
            else:
                target_dir = self.current_dir + "/" + path

        # Нормализуем путь (убираем //, обрабатываем .. и .)
        parts = target_dir.split("/")
        normalized_parts = []

        for part in parts:
            if not part or part == ".":
                continue
            elif part == "..":
                if normalized_parts:
                    normalized_parts.pop()
            else:
                normalized_parts.append(part)

        normalized_path = "/" + "/".join(normalized_parts)
        if not normalized_parts:
            normalized_path = "/"

        # Проверяем существование директории
        real_path = self.get_real_path(normalized_path)

        if not os.path.exists(real_path):
            return f"cd: '{path}': Нет такого файла или директории"

        if not os.path.isdir(real_path):
            return f"cd: '{path}': Это не директория"

        self.current_dir = normalized_path
        return None  # Успех

    def pwd(self):
        return self.current_dir


def execute_script(script_path, vfs):
    try:
        with open(script_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Создаем prompt для отображения команды
                prompt = get_prompt(vfs)
                print(f"{prompt} {line}")
                execute_command(line, vfs)
    except FileNotFoundError:
        print(f"Ошибка: скрипт {script_path} не найден")
    except Exception as e:
        print(f"Ошибка при выполнении скрипта: {e}")


def execute_command(user_input, vfs):
    parts = user_input.split()
    if not parts:
        return

    command = parts[0]
    args = parts[1:]

    if command == "exit":
        print("Выход из эмулятора...")
        sys.exit(0)

    elif command == "ls":
        path = args[0] if args else None
        result = vfs.ls(path)
        if result:
            print(result)

    elif command == "cd":
        path = args[0] if args else "/"
        result = vfs.cd(path)
        if result:
            print(result)

    elif command == "pwd":
        print(vfs.pwd())

    elif command == "conf-dump":
        print("Параметры эмулятора:")
        print(f"  VFS путь: {config.vfs_path}")
        print(f"  Скрипт: {config.script_path}")
        print(f"  Текущая VFS директория: {vfs.current_dir}")

    else:
        print(f"Ошибка: неизвестная команда '{command}'")


def get_prompt(vfs):
    """Генерирует приглашение командной строки с текущей директорией"""
    username = os.getlogin()
    hostname = socket.gethostname()

    # Отображаем текущую директорию VFS
    current_dir = vfs.current_dir
    if current_dir == "/":
        display_dir = "~"
    else:
        display_dir = "~" + current_dir

    return f"{username}@{hostname}:{display_dir}$"


def main():
    parser = argparse.ArgumentParser(description='Эмулятор командной строки UNIX')
    parser.add_argument('--vfs', dest='vfs_path', default='./vfs',
                        help='Путь к физическому расположению VFS')
    parser.add_argument('--script', dest='script_path', default='script.txt',
                        help='Путь к стартовому скрипту')
    global config
    config = parser.parse_args()

    vfs = VFS(config.vfs_path)

    print("=== Параметры эмулятора ===")
    print(f"VFS путь: {config.vfs_path}")
    print(f"Скрипт: {config.script_path}")
    print("===========================")

    print(f"Эмулятор командной строки UNIX")
    print(f"Для выхода введите 'exit'")
    print("-" * 40)

    if config.script_path:
        execute_script(config.script_path, vfs)

    while True:
        prompt = get_prompt(vfs)
        user_input = input(prompt + " ").strip()

        if not user_input:
            continue

        execute_command(user_input, vfs)


if __name__ == "__main__":
    main()