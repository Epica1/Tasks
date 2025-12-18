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
        return list(dependencies.keys())


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
            return list(dependencies.keys())

    except Exception as e:
        raise RuntimeError(f"Failed to read data from file: {e}")


def load_test_graph(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_dependency_graph_dfs(start_package, source_type, source, visited=None, current_path=None, cycles=None):
    if visited is None:
        visited = set()
    if current_path is None:
        current_path = []
    if cycles is None:
        cycles = []

    # Обнаружение циклических зависимостей
    if start_package in current_path:
        cycle_start_index = current_path.index(start_package)
        cycle = current_path[cycle_start_index:] + [start_package]
        cycle_str = " -> ".join(cycle)

        # Добавляем цикл в список, если его еще нет
        if cycle_str not in cycles:
            cycles.append(cycle_str)
            print(f"Cycle detected: {cycle_str}")

        return {}, cycles

    if start_package in visited:
        return {}, cycles

    visited.add(start_package)
    current_path.append(start_package)

    graph = {}

    try:
        # Получаем зависимости в зависимости от типа источника
        if source_type == "test_file":
            dependencies = source.get(start_package, [])
        else:  # registry
            dependencies = get_dependencies_from_registry(start_package, source)

        graph[start_package] = dependencies

        # Рекурсивно обходим все зависимости
        for dep in dependencies:
            sub_graph, sub_cycles = build_dependency_graph_dfs(dep, source_type, source, visited, current_path.copy(),
                                                               cycles)
            graph.update(sub_graph)
            cycles.extend([c for c in sub_cycles if c not in cycles])

    except Exception as e:
        print(f"Error processing package {start_package}: {e}")
        graph[start_package] = []

    current_path.pop()
    return graph, cycles


def main():
    parser = argparse.ArgumentParser()

    # Параметры
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

        # Определяем тип источника и загружаем данные
        if args.test_repo:
            if not args.source.startswith(('http://', 'https://')):
                if not os.path.exists(args.source):
                    raise FileNotFoundError(f"Source file not found: {args.source}")
                graph_source = load_test_graph(args.source)
                source_type = "test_file"
            else:
                graph_source = args.source
                source_type = "registry"
        else:
            if args.source.startswith(('http://', 'https://')):
                graph_source = args.source
                source_type = "registry"
            elif os.path.exists(args.source):
                graph_source = load_test_graph(args.source)
                source_type = "test_file"
            else:
                graph_source = args.source
                source_type = "registry"

        # Построение графа зависимостей с помощью DFS с рекурсией
        dependency_graph, cycles = build_dependency_graph_dfs(args.package, source_type, graph_source)

        # Вывод результатов
        print("\nDependency graph:")
        for package, dependencies in dependency_graph.items():
            if dependencies:
                print(f"{package} -> {', '.join(dependencies)}")
            else:
                print(f"{package} -> No dependencies")

        # Вывод циклических зависимостей
        if cycles:
            print("\nCyclic dependencies found:")
            for i, cycle in enumerate(cycles, 1):
                print(f"  Cycle {i}: {cycle}")
        else:
            print("\nNo cyclic dependencies found")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#python Conf2_3.py --package 'A' --source 'test.txt' --test-repo
