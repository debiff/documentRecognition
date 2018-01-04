from result_statistics.helper import extract_gt_contours, accuracy


def text_statistics(img, p_collector, xml_path, out_path):
    text_coord, non_text_coord = extract_gt_contours(xml_path)
    return accuracy(img, text_coord, out_path, paragraph=p_collector)


def non_text_statistics(img, xml_path, out_path, non_text_img):
    text_coord, non_text_coord = extract_gt_contours(xml_path)
    return accuracy(img, non_text_coord, out_path, non_text_img=non_text_img)
