# Class for reshaping images to a specified size.

from typing import Tuple
import os
from PIL import Image

class ImgReshaper:
    """
    A class to reshape images to a specified size.
    """
    _size: Tuple[int, int]

    def __init__(self, target_size: Tuple[int, int]):
        """
        Initialize the reshaper with a target size.

        :param target_size: The size to which the images will be reshaped.

        ======== Representation Invariant =====
        - target_size is a tuple of two integers representing the width and
        height
        - target_size is a valid size for reshaping images (positive integers)
        """
        self._size = target_size

    def reshape(self, img_name: str, cur_dir: str, new_dir: str) -> None:
        """
        Fetch the image from the current directory, reshape it to the target
        size, and save it in the new directory.

        If the image is larger than the target size, downscale it to fit within
        the target size.

        If the image is smaller than the target size and/or has a different
        aspect ratio, fill the missing parts with white pixels.

        Save the reshaped image under the new image directory as a JPG file.

        ===== Representation Invariant =====
        - image exists at `cur_dir` with the name `img_name`
        - image is a valid image file with the "WebP" format
        """
        img = self._fetch_img(img_name, cur_dir)
        # Downscale if needed
        if self._is_larger(img):
            img = self._downscale_img(img)
        # Fill with white pixels to match target size
        img = self._fill_img(img)
        # Save the reshaped image
        self._save_img(img, new_dir, img_name)

    def _fetch_img(self, img_name: str, cur_dir: str) -> Image:
        """
        Fetch the image from the current directory and return it as a PIL Image
        object.

        :param img_name: The name of the image file to fetch.
        :param cur_dir: The current directory where the image is located.
        :return: A PIL Image object of the fetched image.

        ===== Representation Invariant =====
        - image exists at `cur_dir` with the name `img_name`
        - image is a valid image file with the "WebP" format
        """
        img_path = os.path.join(cur_dir, f"{img_name}.webp")
        return Image.open(img_path)

    def _save_img(self, img: Image, new_dir: str, img_name: str) -> None:
        """
        Save the reshaped image to the new directory as a JPG file.

        :param img: The PIL Image object to save.
        :param new_dir: The directory where the image will be saved.
        :param img_name: The name of the image file to save.

        ===== Representation Invariant =====
        - new_dir is a valid directory path
        - img_name is a valid file name for saving an image
        """
        # Create directory if it doesn't exist
        os.makedirs(new_dir, exist_ok=True)
        save_path = os.path.join(new_dir, f"{img_name}.jpg")

        # Convert to RGB if image has an alpha channel
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency'
                                          in img.info):
            img = img.convert('RGB')

        img.save(save_path, 'JPEG', quality=95)

    def _downscale_img(self, img: Image) -> Image:
        """
        Downscale the image to fit within the target size while maintaining
        aspect ratio.

        :param img: The PIL Image object to downscale.
        :return: A downscaled PIL Image object.
        """
        img_copy = img.copy()
        img_copy.thumbnail(self._size, Image.Resampling.LANCZOS)
        return img_copy

    def _fill_img(self, img: Image) -> Image:
        """
        Fill the image with white pixels to match the target size if it is
        smaller than the target size.

        :param img: The PIL Image object to fill.
        :return: A filled PIL Image object.
        """
        if img.size == self._size:
            return img
        else:
            # Create a white background image
            background = Image.new('RGB', self._size, (255, 255, 255))

            # Calculate position to paste (center the image)
            paste_x = (self._size[0] - img.size[0]) // 2
            paste_y = (self._size[1] - img.size[1]) // 2

            # Paste the original image onto the background
            background.paste(img, (paste_x, paste_y))

            return background

    def _is_larger(self, img: Image) -> bool:
        """
        Check if the image is larger than the target size.

        :param img: The PIL Image object to check.
        :return: True iff the image is larger than the target size
        """
        return (img.size[0] > self._size[0]) or (img.size[1] > self._size[1])

class ImgSquarer(ImgReshaper):
    """
    A class to reshape images to a specified size.
    """
    _size = int

    def __init__(self, target_size: int):
        """
        Initialize the reshaper with a target size.

        :param target_size: The size to which the images will be reshaped.
        """
        super().__init__((target_size, target_size))
