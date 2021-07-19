import json
import os
import re


def merge_json(json_path='../data/json/', output_path='../data/result.json'):
    """
    将多个 json 文件中的数据合并到一个 json 文件中
    :param json_path: json 文件夹的路径，json 文件夹中应含有多个 json 文件
    :param output_path: json 文件保存的路径，应以.json结尾
    """
    print('-' * 64, 'Start the merge_json task', sep='\n')
    json_names = os.listdir(json_path)
    if 'result.json' in json_names:
        json_names.remove('result.json')
    json_names.sort(key=lambda name: int(''.join(re.findall(r'\d', name))))

    # 排除文件夹中非 .json 的文件
    for json_name in json_names.copy():
        if json_name[-4:] != 'json':
            json_names.remove(json_name)

    print('The following is a list of the JSON files that need to be merged: ')
    for json_name in json_names:
        print('\t' + json_name)

    result = {}
    cnt = 0  # 记录下一个 json 文件中第一个数据的序号
    for json_name in json_names:
        json_file = open(os.path.join(json_path, json_name), 'r', encoding='utf-8')
        json_content = json.load(json_file)

        json_content_copy = json_content.copy()
        json_content = {}
        for key, value in json_content_copy.items():
            json_content[int(key) + cnt] = value

        cnt = max(json_content.keys()) + 1
        result.update(json_content)
        json_file.close()

    json_file = open(output_path, 'w', encoding='utf-8')
    json.dump(result, json_file)
    print('The merge_json task is complete, output_path is {}'.format(output_path), '-' * 64, sep='\n')


if __name__ == '__main__':
    os.chdir('D:/WorkSpace/Baidu2021')
    json_path = 'data/json/'
    output_path = 'data/json/result.json'
    merge_json(json_path, output_path)
