#%%
import os
import shutil
import re
from merge_json import merge_json
import json

os.chdir('D:/WorkSpace/Baidu2021')

all_dir_path = 'data/temp'
out_path = 'data/train11'
json_path = 'data/json'

for dir_path in os.listdir(all_dir_path):
    dir_path = os.path.join(all_dir_path, dir_path)

    img_names = os.listdir(dir_path)
    if 'result.json' in img_names:
        img_names.remove('result.json')
    if 'side_cam' in img_names:
        shutil.rmtree(os.path.join(dir_path, 'side_cam'))

    img_names.sort(key=lambda x: int(x.split('.')[0]))

    # 检测 json 和 img 数量是否对应，不对应则做删除操作
    json_file = open(os.path.join(dir_path, 'result.json'))
    json_content = json.load(json_file)
    json_file.close()
    maxID = int(max(json_content.keys(), key=lambda x: int(x)))
    img_names = img_names[:maxID + 1]

    # 确定 startID
    out_names = os.listdir(out_path)
    if 'result.json' in out_names:
        out_names.remove('result.json')
    startID = len(out_names)

    # 复制图片
    for ID, img_name in enumerate(img_names):
        new_imgID = ID + startID
        new_imgName = str(new_imgID) + '.jpg'
        new_imgPath = os.path.join(out_path, new_imgName)
        os.rename(os.path.join(dir_path, img_name), new_imgPath)

    # 复制 json 文件
    json_names = os.listdir(json_path)
    if json_names:
        if 'result.json' in json_names:
            json_names.remove('result.json')
        json_names.sort(key=lambda name: int(''.join(re.findall(r'\d', name))))
        json_id = int(''.join(re.findall(r'\d', json_names[-1]))) + 1
        new_json_name = 'result' + str(json_id) + '.json'
    # shutil.move(os.path.join(dir_path, 'result.json'), 'data/temp')
    else:
        new_json_name = 'result1.json'
    os.rename(os.path.join(dir_path, 'result.json'), os.path.join(json_path, new_json_name))

    # 打印日志
    tip = dir_path.split('/')[-1] + ', ' + new_json_name + ', ' + 'last imgId: ' + str(startID + len(img_names) - 1)
    print(tip)

# 合并生成新 json 文件并移动到目标文件夹
json_path = 'data/json/'
output_path = 'data/json/result.json'
merge_json(json_path, output_path)
shutil.copy(output_path, out_path)
