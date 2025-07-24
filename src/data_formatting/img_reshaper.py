# Class for reshaping images to a specified size.
from typing import Tuple
import os
from PIL import Image

BUFFER_COLOR = (127, 127, 127)

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
        self._buffer_image = Image.new('RGB', self._size, BUFFER_COLOR)
        self._size = target_size

    def reshape(self,
                img_name: str,
                input_directory: str,
                output_directory: str,
                input_extension: str,
                output_extension: str = "jpg") -> str:
        """
        Fetch the image from the current directory, reshape it to the target
        size, and save it in the new directory.

        If the image is larger than the target size, downscale it to fit within
        the target size.

        If the image is smaller than the target size and/or has a different
        aspect ratio, fill the missing parts with white pixels.

        Save the reshaped image under the new image directory with the output
        extension.

        :return: The path to the reshaped image file
        """
        image = self._fetch_img(img_name, input_directory, input_extension)
        image = self._rescale_image(image)
        image = self._fill_img(image)
        return self._save_img(image=image,
                              image_name=img_name,
                              new_directory=output_directory,
                              output_extension=output_extension)

    def _fetch_img(self, img_name: str, cur_dir: str, input_extension: str) -> Image:
        """
        Fetch the image from the current directory and return it as a PIL Image
        object.

        :param img_name: The name of the image file to fetch.
        :param cur_dir: The current directory where the image is located.
        :return: A PIL Image object of the fetched image.
        """
        img_path = os.path.join(cur_dir, f"{img_name}.{input_extension}")
        try:
            with open(img_path , 'rb') as img_file:
                img = Image.open(img_file).load()
            return img
        except Exception as e:
            raise FileNotFoundError(f"Error loading image {img_name} from "
                                    f"{img_path}."
                                    f"Error: {e}")

    def _save_img(self, image: Image, image_name: str, new_directory: str,
                  output_extension: str) -> str:
        """
        Save the new image to the new directory.

        :param image: The PIL Image object to save.
        :param new_directory: The directory where the image will be saved.
        :param image_name: The name of the image file to save.
        :param output_extension: The file extension for the saved image.

        ===== Representation Invariant =====
        - new_dir is a valid directory path
        - img_name is a valid file name for saving an image
        """
        save_path = os.path.join(new_directory, f"{image_name}.{output_extension}")

        try:
            os.makedirs(new_directory, exist_ok=True)
            # If the output format does not support transparency, convert to RGB
            if output_extension.lower() not in ['png', 'gif']:
                image = self._to_rgb(image)
            image.save(save_path, output_extension)
            return save_path
        except Exception as e:
            raise IOError(f"Error saving image {image_name} to {save_path}. "
                          f"Error: {e}")

    def _to_rgb(self, image: Image) -> Image:
        """
        Convert the image to RGB mode if it is in a mode that does not support
        RGB.
        """
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency'
                                            in image.info):
            image = image.convert('RGB')
        return image

    def _rescale_image(self, img):
        """
        Rescale the image to fit within the target size while maintaining
        aspect ratio.
        """

        if self._is_larger(img):
            img = self._downscale_img(img)
        elif self._is_smaller(img):
            img = self._upscale_img(img)
        return img

    def _upscale_img(self, img: Image) -> Image:
        """
        Upscale the image so that one side matches the target size while
        maintaining aspect ratio.

        :param img: The PIL Image object to upscale.
        :return: An upscaled PIL Image object.
        """
        # Calculate scaling factors for width and height
        width_scale = self._size[0] / img.size[0]
        height_scale = self._size[1] / img.size[1]

        # Use the larger scaling factor to ensure at least one side matches target
        scale_factor = max(width_scale, height_scale)

        # Calculate new dimensions
        new_width = int(img.size[0] * scale_factor)
        new_height = int(img.size[1] * scale_factor)

        # Resize the image
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

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
        Fill the image with bugger pixels to match the target size if it is
        smaller than the target size.

        :param img: The PIL Image object to fill.
        :return: A filled PIL Image object.
        """
        # Calculate the position to paste (center the image)
        paste_x = (self._size[0] - img.size[0]) // 2
        paste_y = (self._size[1] - img.size[1]) // 2

        # Paste the image onto the buffer image.
        background = self._buffer_image.copy()
        background.paste(img, (paste_x, paste_y))
        return background

    def _is_larger(self, img: Image) -> bool:
        """
        Check if the image is larger than the target size.

        :param img: The PIL Image object to check.
        :return: True iff any side of the image is above the target size
        """
        return (img.size[0] > self._size[0]) or (img.size[1] > self._size[1])

    def _is_smaller(self, img: Image) -> bool:
        """
        Check if the image is smaller than the target size.

        :param img: The PIL Image object to check.
        :return: True iff both sides of the image are below the target size
        """
        return (img.size[0] < self._size[0]) and (img.size[1] < self._size[1])

class ImgSquarer(ImgReshaper):
    """
    A class to reshape images to a specified size.
    """
    def __init__(self, target_size: int):
        """
        Initialize the reshaper with a target size.

        :param target_size: The size to which the images will be reshaped.
        """
        super().__init__((target_size, target_size))
