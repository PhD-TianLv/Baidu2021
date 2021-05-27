#%%
import os
import shutil

os.chdir('/')

dir_path = 'data/curve_square2'  # param1
img_names = os.listdir(dir_path)
img_names.remove('result.json')

if 'side_cam' in img_names:
    shutil.rmtree(os.path.join(dir_path, 'side_cam'))

img_names.sort(key=lambda x: int(x.split('.')[0]))

startID = 11586 + 1  # param2
# startID = 5000 + 1  # param2
for ID, img_name in enumerate(img_names):
    new_imgID = ID + startID
    new_imgName = str(new_imgID) + '.jpg'
    os.rename(os.path.join(dir_path, img_name), os.path.join(dir_path, new_imgName))
