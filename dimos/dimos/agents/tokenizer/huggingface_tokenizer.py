# Copyright 2025 Dimensional Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from transformers import AutoTokenizer
from dimos.agents.tokenizer.base import AbstractTokenizer
from dimos.utils.logging_config import setup_logger

class HuggingFaceTokenizer(AbstractTokenizer):

    def __init__(self, model_name: str = "Qwen/Qwen2.5-0.5B", **kwargs):
        super().__init__(**kwargs)

        # Initilize the tokenizer for the huggingface models
        self.model_name = model_name
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        except Exception as e:
            raise ValueError(
                f"Failed to initialize tokenizer for model {self.model_name}. Error: {str(e)}"
            )

    def tokenize_text(self, text):
        """
        Tokenize a text string using the openai tokenizer.
        """
        return self.tokenizer.encode(text)

    def detokenize_text(self, tokenized_text):
        """
        Detokenize a text string using the openai tokenizer.
        """
        try:
            return self.tokenizer.decode(tokenized_text, errors="ignore")
        except Exception as e:
            raise ValueError(f"Failed to detokenize text. Error: {str(e)}")

    def token_count(self, text):
        """
        Gets the token count of a text string using the openai tokenizer.
        """
        return len(self.tokenize_text(text)) if text else 0

    @staticmethod
    def image_token_count(image_width, image_height, image_detail="high"):
        """
        Calculate the number of tokens in an image. Low detail is 85 tokens, high detail is 170 tokens per 512x512 square.
        """
        logger = setup_logger(
            "dimos.agents.tokenizer.HuggingFaceTokenizer.image_token_count")

        if image_detail == "low":
            return 85
        elif image_detail == "high":
            # Image dimensions
            logger.debug(
                f"Image Width: {image_width}, Image Height: {image_height}")
            if image_width is None or image_height is None:
                raise ValueError(
                    "Image width and height must be provided for high detail image token count calculation."
                )

            # Scale image to fit within 2048 x 2048
            max_dimension = max(image_width, image_height)
            if max_dimension > 2048:
                scale_factor = 2048 / max_dimension
                image_width = int(image_width * scale_factor)
                image_height = int(image_height * scale_factor)

            # Scale shortest side to 768px
            min_dimension = min(image_width, image_height)
            scale_factor = 768 / min_dimension
            image_width = int(image_width * scale_factor)
            image_height = int(image_height * scale_factor)

            # Calculate number of 512px squares
            num_squares = (image_width // 512) * (image_height // 512)
            return 170 * num_squares + 85
        else:
            raise ValueError(
                "Detail specification of image is not 'low' or 'high'")