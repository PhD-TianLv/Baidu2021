import os
import shutil
import xml.etree.ElementTree as ET


def deleteRedundantPNG():
    for dir_name in os.listdir('./'):
        png_dir = os.path.join('./', dir_name, 'png')
        xml_dir = os.path.join('./', dir_name, 'xml')

        xmlIDs = []
        for xml_name in os.listdir(xml_dir):
            xmlID = int(xml_name.split('.')[0])
            xmlIDs.append(xmlID)

        for png_name in os.listdir(png_dir):
            pngID = int(png_name.split('.')[0])
            if pngID not in xmlIDs:
                os.remove(os.path.join(png_dir, png_name))


def sortPNG_XML():
    for dir_name in os.listdir('./'):
        png_dir = os.path.join('./', dir_name, 'png')
        xml_dir = os.path.join('./', dir_name, 'xml')

        xml_names = sorted(os.listdir(xml_dir), key=lambda x: int(x.split('.')[0]))
        for new_id, xml_name in enumerate(xml_names):
            ID = int(xml_name.split('.')[0])

            # rename XML
            new_xml_name = str(new_id) + '.xml'
            xml_path = os.path.join(xml_dir, xml_name)
            new_xml_path = os.path.join(xml_dir, new_xml_name)
            os.rename(xml_path, new_xml_path)

            # rename PNG
            png_name = str(ID) + '.png'
            new_png_name = str(new_id) + '.png'
            png_path = os.path.join(png_dir, png_name)
            new_png_path = os.path.join(png_dir, new_png_name)
            os.rename(png_path, new_png_path)


def renamePNG_XML():
    dir_name = 'fortress2'
    png_dir = os.path.join('./', dir_name, 'png')
    xml_dir = os.path.join('./', dir_name, 'xml')

    startID = 700 + 1

    xml_names = sorted(os.listdir(xml_dir), key=lambda x: int(x.split('.')[0]))
    for new_id, xml_name in enumerate(xml_names):
        ID = int(xml_name.split('.')[0])
        new_id += startID

        # rename XML
        new_xml_name = str(new_id) + '.xml'
        xml_path = os.path.join(xml_dir, xml_name)
        new_xml_path = os.path.join(xml_dir, new_xml_name)
        os.rename(xml_path, new_xml_path)

        # rename PNG
        png_name = str(ID) + '.png'
        new_png_name = str(new_id) + '.png'
        png_path = os.path.join(png_dir, png_name)
        new_png_path = os.path.join(png_dir, new_png_name)
        os.rename(png_path, new_png_path)


def reform_label(suffix='png'):
    labels = os.listdir('./')
    for label in labels.copy():
        if os.path.isfile(label):
            labels.remove(label)

    train_txt = open('./train.txt', 'w')
    eval_txt = open('./eval.txt', 'w')
    label_list = open('./label_list', 'w')
    label_list_txt = open('./label_list.txt', 'w')

    label_cnt = {}

    for labelID, label in enumerate(labels):
        label_list.write(str(label) + '\n')
        label_list_txt.write(str(labelID) + '\t' + str(label) + '\n')

        xml_dir = os.path.join('./', label, 'xml')
        for xml_name in os.listdir(xml_dir):
            ID = int(xml_name.split('.')[0])
            xml_path = os.path.join(xml_dir, xml_name)
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for elem_obejct in root.iter('object'):
                for elem in elem_obejct.iter('xmin'):
                    xmin = int(elem.text)
                for elem in elem_obejct.iter('ymin'):
                    ymin = int(elem.text)
                for elem in elem_obejct.iter('xmax'):
                    xmax = int(elem.text)
                for elem in elem_obejct.iter('ymax'):
                    ymax = int(elem.text)
                for elem in elem_obejct.iter('name'):
                    name = str(elem.text)

                # 计数
                if name not in label_cnt:
                    label_cnt[name] = 0
                label_cnt[name] += 1

                if label_cnt[name] % 10 == 0:
                    # eval_txt.write(f"data/{name}/{suffix}/{ID}.{suffix}\t{{\"value\":\"{name}\","
                    #                f"\"coordinate\":[[{xmin},{ymin}],[{xmax},{ymax}]]}}\n")
                    eval_txt.write(f'data/{name}/{suffix}/{ID}.{suffix}\tdata/{name}/xml/{ID}.xml\n')
                else:
                    # train_txt.write(f"data/{name}/{suffix}/{ID}.{suffix}\t{{\"value\":\"{name}\","
                    #                 f"\"coordinate\":[[{xmin},{ymin}],[{xmax},{ymax}]]}}\n")
                    train_txt.write(f'data/{name}/{suffix}/{ID}.{suffix}\tdata/{name}/xml/{ID}.xml\n')


def rename_sideData(suffix='png'):
    categories = os.listdir('./')
    for category in categories.copy():
        if os.path.isfile(category):
            categories.remove(category)

    for category in categories:
        png_path = os.path.join(category, suffix)
        img_names = os.listdir(png_path)
        img_names = sorted(img_names, key=lambda name: int(name.split('.')[0]))
        for index, img_name in enumerate(img_names):
            new_name = str(index + 1) + '.' + suffix
            path = os.path.join(png_path, img_name)
            new_path = os.path.join(png_path, new_name)
            os.rename(path, new_path)


def reviseXML(suffix='png'):
    """
    dingxiangjun标签标注错误，进行修改
    """
    categories = os.listdir('./')
    for category in categories.copy():
        if os.path.isfile(category):
            categories.remove(category)

    for category in categories:
        xml_dir_path = os.path.join(category, 'xml')
        xml_names = os.listdir(xml_dir_path)
        xml_names = sorted(xml_names, key=lambda name: int(name.split('.')[0]))
        for xml_name in xml_names:
            xml_path = os.path.join(xml_dir_path, xml_name)
            tree = ET.parse(xml_path)
            root = tree.getroot()

            filename = root.find('filename')
            filename.text = filename.text.split('.')[0] + '.' + suffix

            folder = root.find('folder')
            folder.text = 'png'

            for element in root.findall('object'):
                name = element.find('name')
                name.text = category

            tree.write(xml_path)


def expand_dataset(begin_cnt=51, target_cnt=600):
    """
    通过复制图片和标注文件的方法，扩大数据集
    """
    categories = os.listdir('./')
    for category in categories.copy():
        if os.path.isfile(category):
            categories.remove(category)

    for data_dir in categories:
        cnt = begin_cnt
        ori_amount = cnt - 1

        png_dir = os.path.join(data_dir, 'png')
        xml_dir = os.path.join(data_dir, 'xml')

        while cnt <= target_cnt:
            oriID = cnt % ori_amount if cnt % ori_amount != 0 else ori_amount
            # 复制 png 图片
            png_name = str(oriID) + '.png'
            new_png_name = str(cnt) + '.png'
            png_path = os.path.join(png_dir, png_name)
            new_png_path = os.path.join(png_dir, new_png_name)
            shutil.copy(png_path, new_png_path)

            # 复制并修改 xml 文件
            xml_name = str(oriID) + '.xml'
            new_xml_name = str(cnt) + '.xml'
            xml_path = os.path.join(xml_dir, xml_name)
            new_xml_path = os.path.join(xml_dir, new_xml_name)
            shutil.copy(xml_path, new_xml_path)

            tree = ET.parse(new_xml_path)
            root = tree.getroot()
            filename = root.find('filename')
            filename.text = str(cnt) + '.png'
            tree.write(new_xml_path)

            cnt += 1


if __name__ == '__main__':
    work_dir = 'D:/WorkSpace/Baidu2021'
    dataset_dir = 'data/sideData3'
    os.chdir(os.path.join(work_dir, dataset_dir))

    reform_label()
