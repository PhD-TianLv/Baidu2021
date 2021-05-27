import json

FILE1 = 'train/result.json'
NEW = 'd1.txt'
IMG_DIR = 'd1/'

with open(NEW, 'w') as new:
    with open(FILE1, 'r') as file1:
        label_dict = json.load(file1)
        length = len(label_dict)
        idx = 0
        for name, label in label_dict.items():
            name = IMG_DIR + name + '.jpg'
            new.write(name)
            new.write('\t')
            new.write(str(label))
            if idx != length - 1:
                new.write('\n')
            idx += 1
