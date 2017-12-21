from manager import segmentation
import os

__author__ = 'Simone Biffi'

path = os.path.abspath('./dataset')


recall = 0
precision = 0
i = 0
for filename in os.listdir(path):
    if filename.endswith(".jpg"):
        print(filename + ' - ' + str(i))

        image_path = path + '/' + filename
        r, p = segmentation.run(image_path, filename)
        recall += r
        precision += p
        i += 1
        print('recall: ' + str(r))
        print('precision: ' + str(p))
recall = recall / i
precision = precision / i
f2 = 2 * ((recall * precision) /(recall + precision))
print('average f2 score:' + str(f2))
print('average recall: ' + str(recall))
print('average precision: ' + str(precision))

