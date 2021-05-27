import os
import shutil
import xml.etree.ElementTree as ET

work_dir = 'D:/WorkSpace/Baidu2021'
dataset_dir = 'data/OfficialDataset2021'
os.chdir(os.path.join(work_dir, dataset_dir))


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


def reform_label():
    train_txt = open('./reform_files/train.txt', 'w')
    eval_txt = open('./reform_files/eval.txt', 'w')
    label_list = open('./reform_files/label_list', 'w')
    label_list_txt = open('./reform_files/label_list.txt', 'w')

    label_cnt = {}

    labels = os.listdir('./')
    labels.remove('reform_files')
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
                    eval_txt.write(f"data/{name}/png/{ID}.png\t{{\"value\":\"{name}\","
                                   f"\"coordinate\":[[{xmin},{ymin}],[{xmax},{ymax}]]}}\n")
                else:
                    train_txt.write(f"data/{name}/png/{ID}.png\t{{\"value\":\"{name}\","
                                    f"\"coordinate\":[[{xmin},{ymin}],[{xmax},{ymax}]]}}\n")


if __name__ == '__main__':
    reform_label()
