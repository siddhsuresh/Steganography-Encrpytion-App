import subprocess
from os.path import abspath

import imageio

from image_augmentor import ImageAugmentor

class CoverImageBuilder:
    def __init__(self, image_path: str):
        self.__image_path_ = abspath(image_path)
        self.__output_path_ = self.gen_output_path(self.__image_path_)
        self.__original_pic_ = imageio.imread(self.__image_path_)
        self.__augmentor_ = ImageAugmentor(self.__original_pic_)
        self.__img_ = self.__original_pic_

    def get_output_path(self):
        return self.__output_path_

    @staticmethod
    def remove_exifs(image_path: str) -> str:
        """
        Remove EXIFS from an image.
        :param image_path: Path of the image from which need to remove EXIFS [STR]
        :return:
        """
        if image_path is None:
            raise TypeError
        output = subprocess.run(['exiftool', '-all=', image_path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                shell=False)
        if output.stderr is not None:
            raise OSError
        return output.stdout.decode('utf-8')

    @staticmethod
    def gen_output_path(image_path: str) -> str:
        """
        Builds the output path of the final image.
        :param image_path: Original image path [STR]
        :return: Modified path [STR]
        """
        if image_path is None:
            raise TypeError
        index_last_point = image_path.rindex('.')
        return image_path[:index_last_point] + "_edited.png"

    def build_cover_image(self):
        """
        Builds the cover image:
        1) Performs augmentation
        2) Remove exifs
        """
        augmented_img = self.__augmentor_.get_augmented_image()
        imageio.imwrite(self.__output_path_, augmented_img)
        self.remove_exifs(self.__output_path_)


if __name__ == "__main__":
    ie = CoverImageBuilder("eclipse/resources/test_image.jpg")
    ie.build_cover_image()
