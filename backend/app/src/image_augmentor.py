import imgaug as ia
import imgaug.augmenters as iaa

from eclipse.common import settings as st


def sometimes(aug: iaa):
    """
    Sometimes(0.5, ...) applies the given augmenter in 50% of all cases,
    e.g. Sometimes(0.5, GaussianBlur(0.3)) would blur roughly every second image.
    :param aug: Type of augmentation
    :return: Desired augmentation with a certain probability
    """
    return iaa.Sometimes(0.8, aug)


class ImageAugmentor:
    def __init__(self, img: ia.imageio.core.util.Array):
        self.__original_pic_ = img
        self.__augmented_pic_ = None
        self.__seq_ = iaa.Sequential(
            [
                iaa.Fliplr(st.P_HORIZONTAL_FLIP),
                iaa.Flipud(st.P_VERTICAL_FLIP),  # vertically flip
                # crop images
                sometimes(iaa.CropAndPad(
                    percent=(st.MIN_CROP, st.MAX_CROP),
                    pad_mode=ia.ALL,
                    pad_cval=(0, 255)
                )),
                sometimes(iaa.Affine(
                    # scale images
                    scale={"x": (st.MIN_SCALE, st.MAX_SCALE),
                           "y": (st.MIN_SCALE, st.MAX_SCALE)},
                    # translate
                    translate_percent={
                        "x": (st.MIN_TRANSLATE, st.MAX_TRANSLATE),
                        "y": (st.MIN_TRANSLATE, st.MAX_TRANSLATE)},
                    rotate=(st.MIN_ROTATION, st.MAX_ROTATION),  # rotate
                    shear=(st.MIN_SHEAR, st.MAX_SHEAR),  # shear
                    order=[0, 1],
                    # use nearest neighbour or bilinear interpolation (fast)
                    cval=(0, 255),
                    # if mode is constant, use a cval between 0 and 255
                    mode=ia.ALL
                    # use any of scikit-image's warping modes
                    # (see 2nd image from the top for examples)
                )),
                # execute 0 to 5 of the following (less important) augmenters per image
                # don't execute all of them, as that would often be way too strong
                iaa.SomeOf((0, 5),
                           [
                               # convert images into their superpixel representation
                               sometimes(
                                   iaa.Superpixels(p_replace=(
                                       st.MIN_P_REPLACE_SUPERPIXEL,
                                       st.MAX_P_REPLACE_SUPERPIXEL),
                                       n_segments=(
                                           st.MIN_SUPERPIXELS_PER_IMAGE,
                                           st.MAX_SUPERPIXELS_PER_IMAGE))),
                               iaa.OneOf([
                                   iaa.GaussianBlur(
                                       (st.MIN_BLUR_SIGMA, st.MAX_BLUR_SIGMA)),
                                   # blur images
                                   iaa.AverageBlur(k=(st.MIN_LOCAL_BLUR_SIZE,
                                                      st.MAX_LOCAL_BLUR_SIZE)),
                                   # blur image using local means
                                   # with kernel sizes between 2 and 7
                                   iaa.MedianBlur(k=(3, 11)),
                               ]),
                               iaa.Sharpen(alpha=(
                                   st.MIN_SHARPEN_ALPHA, st.MAX_SHARPEN_ALPHA),
                                   lightness=(0.75, 1.5)),
                               # sharpen images
                               iaa.Emboss(alpha=(
                                   st.MIN_EMBOSS_ALPHA, st.MAX_EMBOSS_ALPHA),
                                   strength=(0, 2.0)),
                               # emboss images
                               # search either for all edges or for directed edges,
                               # blend the result with the original image
                               # using a blobby mask
                               iaa.SimplexNoiseAlpha(iaa.OneOf([
                                   iaa.EdgeDetect(alpha=(
                                       st.MIN_EDGE_DETECTION_ALPHA,
                                       st.MAX_EDGE_DETECTION_ALPHA)),
                                   iaa.DirectedEdgeDetect(alpha=(0.5, 1.0),
                                                          direction=(0.0, 1.0)),
                               ])),
                               iaa.AdditiveGaussianNoise(loc=0, scale=(
                                   0.0, 0.05 * 255), per_channel=0.5),
                               # add gaussian noise to images
                               iaa.OneOf([
                                   iaa.Dropout((st.MIN_DROPOUT, st.MAX_DROPOUT),
                                               per_channel=0.5),
                                   # randomly remove pixels
                                   iaa.CoarseDropout((st.MIN_COARSE_DROPOUT,
                                                      st.MAX_COARSE_DROPOUT),
                                                     size_percent=(0.02, 0.05),
                                                     per_channel=0.2),
                               ]),
                               iaa.Invert(st.P_INVERSION, per_channel=True),
                               # invert color channels
                               iaa.Add((st.MIN_BRIGHTNESS_PURC,
                                        st.MAX_BRIGHTNESS_PURC),
                                       per_channel=0.5),
                               # change brightness of image
                               iaa.AddToHueAndSaturation((st.MIN_HUE_SATURATION,
                                                          st.MAX_HUE_SATURATION)),
                               # change hue and saturation
                               # either change the brightness of the whole image
                               # (sometimes per channel)
                               # or change the brightness of subareas
                               iaa.OneOf([
                                   iaa.Multiply((0.5, 1.5), per_channel=0.5),
                                   iaa.FrequencyNoiseAlpha(
                                       exponent=(-4, 0),
                                       first=iaa.Multiply((0.5, 1.5),
                                                          per_channel=True),
                                       second=iaa.LinearContrast((0.5, 2.0))
                                   )
                               ]),
                               # improve or worsen the contrast
                               iaa.LinearContrast(
                                   (st.MIN_CONTRAST, st.MAX_CONTRAST),
                                   per_channel=0.5),
                               iaa.Grayscale(alpha=(0.0, 1.0)),
                               sometimes(
                                   iaa.ElasticTransformation(alpha=(0.5, 3.5),
                                                             sigma=0.25)),
                               # move pixels locally around (with random strengths)
                               sometimes(iaa.PiecewiseAffine(scale=(
                                   st.MIN_PIECEWISE_SCALE,
                                   st.MAX_PIECEWISE_SCALE))),
                               # sometimes move parts of the image around
                               sometimes(iaa.PerspectiveTransform(
                                   scale=(st.MIN_PERSP_TRANSF_SCALE,
                                          st.MAX_PERSP_TRANSF_SCALE)))
                           ],
                           random_order=True
                           )
            ],
            random_order=True
        )

    def get_augmented_image(self):
        self.__augmented_pic_ = self.__seq_.augment_image(self.__original_pic_)
        return self.__augmented_pic_
