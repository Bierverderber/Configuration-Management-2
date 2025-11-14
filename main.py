import json
import urllib.request
import gzip
from collections import deque

SAMPLE_ARRAY = ["package_name", "repository_url", "test_repository_mode", "version", "output_filename", "ascii_tree_output", "filter_substring"]

def get_data_from_json():
    with open('config.json', 'r', encoding='utf-8') as file: 
        data = json.load(file)
    if len(SAMPLE_ARRAY) == len(data):
        for key in SAMPLE_ARRAY:
            if (key not in data) or (data[key] == ""):
                break
        else:
            return data
    raise ValueError("Неверные значения конфигурации в файле JSON")

def display_data(data):
    print("\n=== Configurations ===")
    for key, value in data.items():
        print(f"{key}: {value}")

def get_package_dependencies(config, package_name, version, version_mode=True):
    if config["test_repository_mode"]:
        return get_test_dependencies(config, package_name)
    else:
        return get_real_dependencies(config, package_name, version, version_mode)

def get_real_dependencies(config, package_name, version, version_mode=True):
    repository_url = config["repository_url"]
    
    packages_gz_url = f"{repository_url}/Packages.gz"
    urllib.request.urlretrieve(packages_gz_url, "Packages.gz")
    
    with gzip.open('Packages.gz', 'rt', encoding='utf-8') as f:
        content = f.read()
    
    packages = content.split('\n\n')
    
    for package in packages:
        lines = package.split('\n')
        found_package = None
        found_version = None
        depends = None
        
        for line in lines:
            if line.startswith('Package:'):
                found_package = line.split(':', 1)[1].strip()
            elif line.startswith('Version:'):
                found_version = line.split(':', 1)[1].strip()
            elif line.startswith('Depends:'):
                depends = line.split(':', 1)[1].strip()
        
        if found_package == package_name and (version == found_version or not version_mode):
            if depends:
                dependencies = []
                for depend in depends.split(','):
                    depend_name = depend.strip().split(' ')[0]
                    if depend_name and depend_name not in dependencies:
                        dependencies.append(depend_name)
                return dependencies
            else:
                return []
    
    raise ValueError(f"Package {package_name} version {version} was not found")

def get_test_dependencies(config, package_name):
    repo_file = config["repository_url"]
    with open(repo_file, 'r') as f:
        content = f.read()
    
    packages = content.split('\n\n')
    
    for package in packages:
        lines = package.split('\n')
        found_package = None
        depends = None
        
        for line in lines:
            if line.startswith('Package:'):
                found_package = line.split(':', 1)[1].strip()
            elif line.startswith('Depends:'):
                depends = line.split(':', 1)[1].strip()
        
        if found_package == package_name:
            if depends:
                return [dep.strip() for dep in depends.split(',')]
            else:
                return []
    
    return []

def get_all_packages_dependencies(config):
    if config["test_repository_mode"]:
        repo_file = config["repository_url"]
        with open(repo_file, 'r') as f:
            content = f.read()
    else:
        repository_url = config["repository_url"]
        packages_gz_url = f"{repository_url}/Packages.gz"
        urllib.request.urlretrieve(packages_gz_url, "Packages.gz")
        with gzip.open('Packages.gz', 'rt', encoding='utf-8') as f:
            content = f.read()
    
    all_deps = {}
    packages = content.split('\n\n')
    
    for package in packages:
        lines = package.split('\n')
        found_package = None
        depends = None
        
        for line in lines:
            if line.startswith('Package:'):
                found_package = line.split(':', 1)[1].strip()
            elif line.startswith('Depends:'):
                depends = line.split(':', 1)[1].strip()
        
        if found_package:
            if depends:
                dependencies = []
                for depend in depends.split(','):
                    depend_name = depend.strip().split(' ')[0]
                    if depend_name and depend_name not in dependencies:
                        dependencies.append(depend_name)
                all_deps[found_package] = dependencies
            else:
                all_deps[found_package] = []
    
    return all_deps

def build_dependency_graph(config):
    start_package = config["package_name"]
    version = config["version"]
    filter_str = config["filter_substring"]
    cnt = 0
    
    graph = {}
    visited = set()
    queue = deque([start_package])
    
    while queue:
        current_package = queue.popleft()
        
        if current_package in visited:
            continue
            
        visited.add(current_package)
        
        if filter_str and filter_str in current_package:
            graph[current_package] = []
            continue
        if cnt == 0:
            dependencies = get_package_dependencies(config, current_package, version)
        else:
            dependencies = get_package_dependencies(config, current_package, version, False)
        
        filtered_deps = []
        for dep in dependencies:
            if not (filter_str and filter_str in dep):
                filtered_deps.append(dep)
                if dep not in visited:
                    queue.append(dep)
        
        graph[current_package] = filtered_deps

        cnt += 1
    
    return graph

def find_reverse_dependencies(config, target_package):
    all_deps = get_all_packages_dependencies(config)
    filter_str = config["filter_substring"]
    
    reverse_deps = []
    
    for package, dependencies in all_deps.items():
        if filter_str and filter_str in package:
            continue
        
        if target_package in dependencies:
            reverse_deps.append(package)
    
    return reverse_deps

def display_dependency_graph(graph):
    print("\n=== Full Dependency Graph ===")
    for package, dependencies in graph.items():
        if dependencies:
            print(f"{package} -> {', '.join(dependencies)}")
        else:
            print(f"{package} -> No dependencies")

def display_dependencies(dependencies, title="Direct dependencies"):
    print(f"\n=== {title} ===")
    if dependencies:
        for i in range(1, len(dependencies) + 1):
            print(f"{i}. {dependencies[i - 1]}")
    else:
        print("No dependencies found")

if __name__ == "__main__":
    config = get_data_from_json()
    display_data(config)
    
    dependencies = get_package_dependencies(config, config["package_name"], config["version"])
    display_dependencies(dependencies)
    
    graph = build_dependency_graph(config)
    display_dependency_graph(graph)
    
    reverse_deps = find_reverse_dependencies(config, config["package_name"])
    display_dependencies(reverse_deps, "Reverse dependencies")