import json

def load_config():
    with open("./config.json", "r") as file:
        return json.load(file)

if __name__ == "__main__":
    print(load_config())
