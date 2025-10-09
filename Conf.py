import os  # модуль os для взаимодействия с операционной системой(получение имени пользователя)
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