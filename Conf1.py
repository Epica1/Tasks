
import argparse
import sys
import os


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--package', type=str, required=True)
    parser.add_argument('--source', type=str, required=True)
    parser.add_argument('--test-repo', action='store_true')
    parser.add_argument('--tree', action='store_true')

    try:
        args = parser.parse_args()

        if not args.package or not args.package.strip():
            raise ValueError("Package name cannot be empty")

        if not args.source or not args.source.strip():
            raise ValueError("Source cannot be empty")

        if args.test_repo and not args.source.startswith(('http://', 'https://')):
            if not os.path.exists(args.source):
                raise FileNotFoundError(f"Source file not found: {args.source}")

        print("Конфигурация приложения:")
        print(f"  Пакет: {args.package}")
        print(f"  Источник: {args.source}")
        print(f"  Тестовый режим: {args.test_repo}")
        print(f"  Режим дерева: {args.tree}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
