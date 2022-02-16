def get_keys():
    sensitive = {}
    f = open("./sensitive.txt", "r")
    for line in f:
        (key, value) = line.split(",")
        sensitive[key] = value

sensitive = get_keys()