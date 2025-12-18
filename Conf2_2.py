import argparse
import sys
import os
import urllib.request
import json


def get_dependencies_from_registry(package_name, source_url):
    # Формирование url запроса
    base_url = source_url.rstrip('/')
    url = f"{base_url}/{package_name}"

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

        # Получение версии пакета
        latest_version = data.get('dist-tags', {}).get('latest')
        if not latest_version:
            raise ValueError(f"Latest version not found for package {package_name}")
        # Извлечение зависимостей
        versions = data.get('versions', {})
        dependencies = versions[latest_version].get('dependencies', {})
        return dependencies


def get_dependencies_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Аналогичная логика извлечения зависимостей
            latest_version = data.get('dist-tags', {}).get('latest')
            if not latest_version:
                raise ValueError("Latest version not found in test file")

            versions = data.get('versions', {})
            dependencies = versions[latest_version].get('dependencies', {})
            return dependencies

    except FileNotFoundError:
        raise FileNotFoundError(f"Source file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error parsing JSON from file: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to read data from file: {e}")

def main():
    parser = argparse.ArgumentParser()

    # Параметры
    parser.add_argument('--package', type=str, required=True)
    parser.add_argument('--source', type=str, required=True)
    parser.add_argument('--test-repo', action='store_true')
    parser.add_argument('--tree', action='store_true')
    args = parser.parse_args()

    try:
        if not args.package or not args.package.strip():
            raise ValueError("Package name cannot be empty")

        if not args.source or not args.source.strip():
            raise ValueError("Source cannot be empty")

        if args.test_repo and not args.source.startswith(('http://', 'https://')):
            if not os.path.exists(args.source):
                raise FileNotFoundError(f"Source file not found: {args.source}")

        if args.test_repo:
            dependencies = get_dependencies_from_file(args.source)
        else:
            dependencies = get_dependencies_from_registry(args.package, args.source)

        if dependencies:
            print("Direct dependencies:")
            for dep, version in dependencies.items():
                print(f"{dep}: {version}")
        else:
            print("No direct dependencies found")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#'https://registry.npmjs.org/'