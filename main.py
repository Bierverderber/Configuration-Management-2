import json

SAMPLE_ARRAY = ["package_name", "repository_url", "test_repository_mode", "version", "output_filename", "ascii_tree_output", "filter_substring"]

def test():
    with open('config.json', 'r', encoding='utf-8') as file: 
        data = json.load(file)
        print(data)


def get_data_from_json():
    with open('config.json', 'r', encoding='utf-8') as file: 
        data = json.load(file)
    if len(SAMPLE_ARRAY) == len(data):
        for key in SAMPLE_ARRAY:
            if (key not in data) or (data[key] == ""):
                break
        else:
            return data
    raise ValueError("Неверные значения конфигурации в фалйе JSON")
    return -1

def display_data(data):
    print("\n=== Configurations ===")
    for key, value in data.items():
        print(f"{key}: {value}\n")


if __name__ == "__main__":
    display_data(get_data_from_json())