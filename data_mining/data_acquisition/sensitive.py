def get_keys():
    sensitive = {}
    f = open("./Data Acquisition/sensitive.txt", "r")
    for line in f:
        (key, value) = line.split(",")
        sensitive[key] = value
    return sensitive
