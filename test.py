__author__ = 'Simone Biffi'

from datetime import datetime
import numpy as np
import cv2
from helper import component, image
from MHS import cc_analysis, heuristic_filter, recursive_filter
from MHS.classes import component as comp

timer = datetime.now()

# loads the image and convert to grayscale
img, gray = image.load_and_gray('./samples/icdar.jpg')
binary = image.binarize(gray)

# finds component through findcontours
contours, hierarchy = component.find_component(binary)

print((datetime.now()-timer))
rect, cc_arr = cc_analysis.create_component(contours, 6, 0.15)
print((datetime.now()-timer))

#Textmask = np.ones(img.shape[:2], dtype="uint8") * 255
NonTextmask = np.ones(img.shape[:2], dtype="uint8") * 255
text_element, non_text_element = heuristic_filter.heuristic_f(rect, 4)
cc_arr_text = cc_arr[list(text_element.keys())]

for index, cc in text_element.items():
    if cc[0].inner_components > 1:
        cv2.drawContours(NonTextmask, [cc[0].contour], -1, 0, cv2.FILLED)
    else:
        cv2.drawContours(NonTextmask, [cc[0].contour], -1, 0, cv2.FILLED)

kernel = np.ones((5, 5), np.uint8)
dilation = cv2.erode(NonTextmask, kernel, iterations=1)
cv2.imwrite('./samples/test_erosion.png', dilation)
    #cv2.drawContours(NonTextmask, [cc[0].get_contour()], -1, 0, cv2.FILLED)
    #component.draw_rect(img, cc[0].get_xmin(), cc[0].get_ymin(), cc[0].get_xmax(), cc[0].get_ymax(), (36, 127, 227))

#for index, cc in non_text_element.items():
    #component.draw_rect(img, cc[0].get_xmin(), cc[0].get_ymin(), cc[0].get_xmax(), cc[0].get_ymax(), (12, 127, 19))

#hom_region = recursive_filter.run(NonTextmask, True, './samples/split/')
hom_region = []
final_region = []
hom_region.append((dilation, (0, 0, NonTextmask.shape[1], NonTextmask.shape[0]), list(text_element.keys())))
splitted = True
textMask = np.ones(binary.shape[:2], dtype="uint8") * 255
while splitted:
    splitted = False
    tmp_region = []
    for j, r in enumerate(hom_region):
        recursive = recursive_filter.run(r[0], False, './samples/split/')
        for index, region in enumerate(recursive):
            tmp_cc = comp.Component(index, region[1][0][0], region[1][0][1], region[1][0][2], region[1][0][3])
            inner = cc_analysis.inner_bb(cc_arr[r[2]], tmp_cc)
            included = {x: text_element[r[2][x]] for x in inner}
            areatot_list = []
            wtot_list = []
            htot_list = []
            ws_list = []
            candidate_list = []
            for key, value in included.items():
                areatot_list.append((key, value[0].area))
                wtot_list.append((key, value[0].bb_width))
                htot_list.append((key, value[0].bb_height))
                r_nn_distance = rect[value[0].nnr][0].xmin - value[0].xmax \
                    if value[0].nnr > -1 else 0
                l_nn_distance = value[0].xmin - rect[value[0].nnl][0].xmax \
                    if value[0].nnl > -1 else 0
                ws_list.append((key, r_nn_distance, l_nn_distance))

            mod = True
            add = False
            while mod:
                mod = False
                if len(included) > 0:
                    areatot = np.array(areatot_list)
                    area_mean = np.mean(areatot[:, 1])
                    area_median = np.median(areatot[:, 1])
                    area_max = np.argmax(areatot[:, 1])
                    area_min = np.argmin(areatot[:, 1])
                    area_t = max((area_mean/area_median), (area_median/area_mean))

                    if areatot[area_max][1] > (area_t * area_median):
                        wtot = np.array(wtot_list)
                        w_mean = np.mean(wtot[:, 1])
                        w_median = np.median(wtot[:, 1])
                        w_max = np.argmax(wtot[:, 1])
                        w_t = max((w_mean / w_median), (w_median / w_mean))

                        htot = np.array(htot_list)
                        h_mean = np.mean(htot[:, 1])
                        h_median = np.median(htot[:, 1])
                        h_max = np.argmax(wtot[:, 1])
                        h_t = max((h_mean / h_median), (h_median / h_mean))

                        if (wtot[area_max][1] > (w_t * w_median) and wtot[area_max][1] == wtot[w_max][1]) or (htot[area_max][1] > (h_t * h_median) and htot[area_max][1] == htot[h_max][1]):
                            ws = np.array(ws_list)
                            ws_mean = np.mean(ws[:, 1])
                            ws_median = np.median(ws[:, 1])
                            ws_max = np.argmax(ws[:, 1])
                            if ( (min(ws[area_max][1], ws[area_max][2]) > max(ws_mean, ws_median)) and \
                                ((max(ws[area_max][1], ws[area_max][2]) >= ws_max) or \
                                 (min(ws[area_max][1], ws[area_max][2]) > (2 * ws_mean))) )\
                                    or max(len(included[areatot[area_max][0]][0].nr), len(included[areatot[area_max][0]][0].nl)) > 2:
                                areatot_list.pop(area_max)
                                wtot_list.pop(area_max)
                                htot_list.pop(area_max)
                                ws_list.pop(area_max)
                                del included[areatot[area_max][0]]
                                mod = True
                                add = True
                    elif areatot[area_min][1] < (area_median / area_t):
                        wtot = np.array(wtot_list)
                        w_mean = np.mean(wtot[:, 1])
                        w_median = np.median(wtot[:, 1])
                        w_max = np.argmax(wtot[:, 1])
                        w_min = np.argmin(wtot[:, 1])
                        w_t = max((w_mean / w_median), (w_median / w_mean))

                        htot = np.array(htot_list)
                        h_mean = np.mean(htot[:, 1])
                        h_median = np.median(htot[:, 1])
                        h_max = np.argmax(wtot[:, 1])
                        h_min = np.argmin(wtot[:, 1])
                        h_t = max((h_mean / h_median), (h_median / h_mean))

                        if (wtot[area_min][1] < (w_median / w_t )) or (htot[area_min][1] < (h_median / h_t)):
                            ws = np.array(ws_list)
                            ws_mean = np.mean(ws[:, 1])
                            ws_median = np.median(ws[:, 1])
                            ws_max = np.argmax(ws[:, 1])
                            if ( (min(ws[area_min][1], ws[area_min][2]) > max(ws_mean, ws_median)) and \
                                ((max(ws[area_min][1], ws[area_min][2]) >= ws_max) or \
                                 (min(ws[area_min][1], ws[area_min][2]) > (2 * ws_mean))) )\
                                    or max(len(included[areatot[area_min][0]][0].nr), len(included[areatot[area_min][0]][0].nl)) > 2:
                                areatot_list.pop(area_min)
                                wtot_list.pop(area_min)
                                htot_list.pop(area_min)
                                ws_list.pop(area_min)
                                del included[areatot[area_min][0]]
                                mod = True
                                add = True
            if add:
                tmp_mask = np.ones(region[0].shape[:2], dtype="uint8") * 255
                for key, value in included.items():
                    contour = value[0].contour
                    if value[0].inner_components > 1:
                        cv2.drawContours(textMask, [contour], -1, 0, cv2.FILLED)
                    else:
                        cv2.drawContours(textMask, [contour], -1, 0, cv2.FILLED)

                for key, value in included.items():
                    contour = value[0].contour
                    contour[:, 0][:, 0] = contour[:, 0][:, 0] - region[1][0][0]
                    contour[:, 0][:, 1] = contour[:, 0][:, 1] - region[1][0][1]
                    if value[0].inner_components > 1:
                        cv2.drawContours(tmp_mask, [contour], -1, 0, cv2.FILLED)
                    else:
                        cv2.drawContours(tmp_mask, [contour], -1, 0, cv2.FILLED)
                tmp_region.append((tmp_mask, region[1], list(included.keys())))
            else:
                final_region.append((region[0], region[1], list(included.keys())))
                for key, value in included.items():
                    contour = value[0].contour
                    if value[0].inner_components > 1:
                        cv2.drawContours(textMask, [contour], -1, 0, cv2.FILLED)
                    else:
                        cv2.drawContours(textMask, [contour], -1, 0, cv2.FILLED)

    if len(tmp_region) != 0:
        splitted = True
        hom_region = tmp_region


for i, r in enumerate(final_region):
    cv2.imwrite('./samples/split/final' + str(i) + '.png', r[0])

cv2.imwrite('./samples/split/textMask.png', textMask)
not_text = np.bitwise_not(textMask)
not_text[not_text == 0] = 1
not_text[not_text == 255] = 0
binary[binary == 0] = 1
binary[binary == 255] = 0
np.bitwise_and(binary, not_text, textMask)
textMask[textMask == 0] = 255
textMask[textMask == 1] = 0
kernel = np.ones((15,15), np.uint8)
dilation = cv2.dilate(np.bitwise_not(textMask),kernel,iterations = 1)
cv2.imwrite('./samples/split/dilation.png', dilation)
cv2.imwrite('./samples/split/text.png', textMask)

#text = cv2.bitwise_and(binary, binary, mask=NonTextmask)
#text = cv2.bitwise_and(binary, NonTextmask)
#nonText = cv2.bitwise_and(img, img, mask = cv2.bitwise_not(Textmask))
#cv2.imwrite('./samples/textElement.png', text)
#cv2.imwrite('./samples/textElementMask.png', Textmask)
#cv2.imwrite('./samples/nontextElementMask.png', nonText)

print((datetime.now()-timer))



