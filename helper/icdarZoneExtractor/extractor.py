import os
import xml.etree.ElementTree as ET
import cv2
import numpy as np


path = '../../dataset'
for filename in os.listdir(path):
    if filename.endswith(".jpg"):
        image_path = path + '/' + filename
        xml_path = path + '/pc-' + filename.replace('.jpg', '.xml')

        img = cv2.imread(image_path, -1)

        tree = ET.parse(xml_path)
        root = tree.getroot()
        for child in root[1]:
            try:
                polygon = []
                xmin = 999999
                xmax = 0
                ymin = 9999999
                ymax = 0
                for coord in child[0]:
                    for axe, value in coord.attrib.items():
                        if axe == 'x':
                            x = int(value)
                            xmin = min(xmin, x)
                            xmax = max(xmax, x)
                        else:
                            y = int(value)
                            ymin = min(ymin, y)
                            ymax = max(ymax, y)
                    polygon.append((x, y))
                mask = np.zeros(img.shape, dtype=np.uint8)
                pts = np.array(polygon, dtype=np.int32)
                channel_count = img.shape[2]
                ignore_mask_color = (255,) * channel_count
                cv2.fillConvexPoly(mask, pts, ignore_mask_color)
                masked_image = cv2.bitwise_and(img, mask)

                if child.tag.find('TextRegion') != -1:
                    out_path = '/Region/TextRegion/' + child.attrib['type']
                else:
                    out_path = '/Region/NonTextRegion/' + child.tag.split("}")[1]
                out_path = path + out_path
                if not os.path.exists(out_path):
                    os.makedirs(out_path)
                out_path = out_path + "/" + filename.split(".")[0] + "_" + child.attrib['id'] + ".png"

                cv2.imwrite(out_path, masked_image[ymin:ymax, xmin:xmax, :])

            except Exception as e:
                print(e)
