import os # модуль os для взаимодействия с операционной системой(получение имени пользователя)
import socket # для работы с сетевыми соединениями (получение имени хоста)


def main():
    username = os.getlogin() # возвращает имя текущего пользователя
    hostname = socket.gethostname() # возвращает имя текущего хоста

    print(f"Эмулятор командной строки UNIX")
    print(f"Для выхода введите 'exit'")
    print("-" * 40)

    while True: # бесконечный цикл работает, пока не будет введена команда exit
        prompt = f"{username}@{hostname}:~$ "
        user_input = input(prompt).strip()

        if not user_input:
            continue #переход к следующему этапу, если введена пустая строка

        parts = user_input.split()# азбивает введеную строку на список слов по пробелу
        command = parts[0] #первое слово является командой
        args = parts[1:] # остальное аргументы

        if command == "exit":
            print("Выход из эмулятора...")
            break

        elif command == "ls":
            print(f"Команда: ls, аргументы: {args}")

        elif command == "cd":
            print(f"Команда: cd, аргументы: {args}")

        else:
            print(f"Ошибка: неизвестная команда '{command}'")


if __name__ == "__main__": #запуск программы
    main()