import json
import urllib.request
import gzip

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

def get_package_dependencies(config):
    package_name = config["package_name"]
    repository_url = config["repository_url"]
    version = config["version"]
    
    print(f"\nDependency search for: {package_name} version {version}")
    print(f"Repository: {repository_url}")
    
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
        
        if found_package == package_name and version == found_version:
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

def display_dependencies(dependencies):
    print("\n=== Direct dependencies ===")
    if dependencies:
        for i in range(1, len(dependencies) + 1):
            print(f"{i}. {dependencies[i - 1]}")
    else:
        print("No dependencies found")

if __name__ == "__main__":
    config = get_data_from_json()
    display_data(config)
    
    dependencies = get_package_dependencies(config)
    display_dependencies(dependencies)