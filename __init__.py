from manager import segmentation
import os

__author__ = 'Simone Biffi'

path = os.path.abspath('./dataset')

recall_txt = 0
precision_txt = 0
recall_n_txt = 0
precision_n_txt = 0
i = 0
for filename in os.listdir(path):
    if filename.endswith(".jpg"):
        print(filename + ' - ' + str(i))

        image_path = path + '/' + filename
        r_txt, p_txt, r_n_txt, p_n_txt = segmentation.run(image_path, filename)
        if r_txt == 0 or p_txt == 0 or r_n_txt == 0 or p_n_txt == 0:
            print('error in calculus')
        else:
            recall_txt += r_txt
            precision_txt += p_txt
            recall_n_txt += r_n_txt
            precision_n_txt += p_n_txt
            i += 1
            print('recall_txt: ' + str(r_txt))
            print('precision_txt: ' + str(p_txt))
            print('recall_n_txt: ' + str(r_n_txt))
            print('precision_n_txt: ' + str(p_n_txt))
recall_txt = recall_txt / i
precision_txt = precision_txt / i
f2_txt = 2 * ((recall_txt * precision_txt) / (recall_txt + precision_txt))
print('average f2_txt score:' + str(f2_txt))
print('average recall_txt: ' + str(recall_txt))
print('average precision_txt: ' + str(precision_txt))

recall_n_txt = recall_n_txt / i
precision_n_txt = precision_n_txt / i
f2_n_txt = 2 * ((recall_n_txt * precision_n_txt) /(recall_n_txt + precision_n_txt))
print('average f2_n_txt score:' + str(f2_n_txt))
print('average recall_n_txt: ' + str(recall_n_txt))
print('average precision_n_txt: ' + str(precision_n_txt))

