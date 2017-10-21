__author__ = 'Simone Biffi'

import cv2
from skimage import io
from skimage.viewer import ImageViewer


def load_and_show(path, gray=False, show=False):
    # set the grayscale value

    grayscale = cv2.IMREAD_COLOR
    if gray:
        # if gray == True, want to load a grayscale image
        grayscale = cv2.IMREAD_GRAYSCALE

    # load the image
    img = cv2.imread(path, grayscale)

    if show:
        # The advantage of ImageViewer compare to skimage.io.imshow  is that I can
        # easily add plugins for manipulating images
        viewer = ImageViewer(img)
        viewer.show()

    return img


def binarize(img, path_out=None, show=False):
    # img must be grayscale image
    if not is_grayscale(img):
        raise ValueError('The image should be a grayscale image')

    ret2, th2 = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # save grayscale image if there is a path
    if path_out != None:
        io.imsave(path_out, th2)

    return th2


def is_grayscale(img):
    # if an image is grayscale has 2 channels so the dimension is < 3
    # if an image is RGB has 3 channels so the dimension is 3
    if len(img.shape) < 3:
        return True
    return False


def load_and_gray(path):
    # load the image
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img, gray


# return the orginal image and the grayscale image of the downsampled image
def load_downsample_gray(path):
    # load the image
    img = cv2.imread(path)
    sampled = cv2.pyrDown(img)
    gray = cv2.cvtColor(sampled, cv2.COLOR_BGR2GRAY)
    return img, sampled, gray
