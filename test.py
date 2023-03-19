import csv

file = r'D:\projects\foodgram-project-react\data\ingredients.json'
with open(file, encoding='utf-8') as r_file:
    data = csv.reader(r_file, delimiter=",")
    for ing in data:
        for i in ing:
            print(i)
        