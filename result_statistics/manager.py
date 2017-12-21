from result_statistics.helper import extract_gt_contours, accuracy


def text_statistics(img, p_collector, xml_path, out_path):
    text_coord, non_text_coord = extract_gt_contours(xml_path)
    return accuracy(img, p_collector, text_coord, out_path)
