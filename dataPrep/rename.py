#%%
import os

os.chdir('D:\\WorkSpace\\Baidu2021')
#%%
dir_path = 'data/train_5' # param1
img_names = os.listdir(dir_path)
img_names.remove('result.json')
#%%
img_names.sort(key=lambda x: int(x.split('.')[0]))

startID = 4372 + 1 # param2
for img_name in img_names:
    imgID = int(img_name.split('.')[0])
    new_imgID = imgID + startID
    new_imgName = str(new_imgID) + '.jpg'
    os.rename(os.path.join(dir_path, img_name), os.path.join(dir_path, new_imgName))
