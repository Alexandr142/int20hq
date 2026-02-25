import json


def concat_json_databases(filenames, output_filename):
    new_database = []
    for fn in filenames:
        with open("data/" + fn, 'r') as file:
            new_database += json.load(file)
    for i in range(len(new_database)):
        new_database[i]["id"] = i + 1
    with open("data/" + output_filename, 'w') as file:
        json.dump(new_database, file, indent=4)
