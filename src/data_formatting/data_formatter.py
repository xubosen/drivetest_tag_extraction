from entities.question_bank import QuestionBank
from data_formatting.img_reshaper import ImgReshaper
from pydantic import BaseModel, Field, field_validator

VALID_EXTENSIONS = {"jpg", "jpeg", "webp", "png", "bmp", "gif"}


class DataFormat(BaseModel):
    """
    Data format for the question bank.
    """
    image_shape: tuple[int, int] = Field(default=(256, 256),
                                         min_length=2,
                                         max_length=2,
                                         description="Size to which images "
                                                     "will be reshaped.")
    input_image_extension: str = Field(..., description="Extension of the input"
                                                        " images.")
    output_image_extension: str = Field(..., description="Extension of the "
                                                         "output images.")

    @field_validator("image_shape", mode="before")
    @classmethod
    def validate_image_shape(cls, value: tuple[int, int]) -> tuple[int, int]:
        """
        Validate that the image shape is a tuple of two positive integers above
        or equal to 28.
        """
        if not isinstance(value, tuple):
            raise ValueError("Image shape must be a tuple of two integers.")
        for val in value:
            if not isinstance(val, int) or val < 28:
                raise ValueError(f"Image shape values must be integers "
                                 f"greater than or equal to 28: {value}.")
        return value

    @field_validator("input_image_extension",
                     "output_image_extension")
    @classmethod
    def validate_extensions(cls, extension: str) -> str:
        """
        Validate that the input and output image extensions are valid.
        """
        if extension.lower() not in VALID_EXTENSIONS:
            raise ValueError(f"Invalid image extension: {extension}. "
                             f"Valid extensions are: {VALID_EXTENSIONS}.")
        return extension.lower()

class DataFormatter:
    """
    Class of objects that formats the question bank object for automatic
    labeling.
    """
    _data_format: DataFormat

    def __init__(self, data_format: DataFormat):
        """
        Initializes the DataFormatter with the output directory.
        """
        if not isinstance(data_format, DataFormat):
            raise TypeError(
                f"Invalid data format: {data_format}. "
                f"Expected instance of DataFormat."
            )
        self._data_format = data_format

    def format_data(self, question_bank: QuestionBank,
                    new_img_dir: str) -> QuestionBank:
        """
        Formats the question bank for automatic labeling.
        """
        self._resize_images(qb=question_bank,
                            new_img_dir=new_img_dir,
                            reshaper=ImgReshaper(
                                target_size=self._data_format.image_shape
                            ))
        return question_bank

    def _resize_images(self, qb: QuestionBank, new_img_dir: str,
                       reshaper: ImgReshaper) -> None:
        """ Resize images in the question bank and update their paths. """
        for qid in qb.get_qid_list():
            question = qb.get_question(qid)
            if question.has_img():
                new_path = (
                    reshaper.reshape(img_name=qid,
                                     input_directory=qb.get_img_dir(),
                                     output_directory=new_img_dir,
                                     input_extension=
                                     self._data_format.input_image_extension,
                                     output_extension=
                                     self._data_format.output_image_extension))
                question.set_img_path(new_path)
        qb.set_img_dir(new_img_dir)
