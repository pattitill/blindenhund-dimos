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

"""
Image embedding module for converting images to vector embeddings.

This module provides a class for generating vector embeddings from images
using pre-trained models like CLIP, ResNet, etc.
"""

import os
import logging
import numpy as np
from typing import Union, List, Dict, Any
from PIL import Image
import io
import cv2
import base64
from dimos.utils.logging_config import setup_logger

logger = setup_logger("dimos.agents.memory.image_embedding")

class ImageEmbeddingProvider:
    """
    A provider for generating vector embeddings from images.
    
    This class uses pre-trained models to convert images into vector embeddings
    that can be stored in a vector database and used for similarity search.
    """
    
    def __init__(self, model_name: str = "clip", dimensions: int = 512):
        """
        Initialize the image embedding provider.
        
        Args:
            model_name: Name of the embedding model to use ("clip", "resnet", etc.)
            dimensions: Dimensions of the embedding vectors
        """
        self.model_name = model_name
        self.dimensions = dimensions
        self.model = None
        self.processor = None
        
        self._initialize_model()
        
        logger.info(f"ImageEmbeddingProvider initialized with model {model_name}")
    
    def _initialize_model(self):
        """Initialize the specified embedding model."""
        try:
            import torch
            from transformers import CLIPProcessor, CLIPModel, AutoFeatureExtractor, AutoModel
            
            if self.model_name == "clip":
                model_id = "openai/clip-vit-base-patch32"
                self.model = CLIPModel.from_pretrained(model_id)
                self.processor = CLIPProcessor.from_pretrained(model_id)
                logger.info(f"Loaded CLIP model: {model_id}")
            elif self.model_name == "resnet":
                model_id = "microsoft/resnet-50"
                self.model = AutoModel.from_pretrained(model_id)
                self.processor = AutoFeatureExtractor.from_pretrained(model_id)
                logger.info(f"Loaded ResNet model: {model_id}")
            else:
                raise ValueError(f"Unsupported model: {self.model_name}")
        except ImportError as e:
            logger.error(f"Failed to import required modules: {e}")
            logger.error("Please install with: pip install transformers torch")
            # Initialize with dummy model for type checking
            self.model = None
            self.processor = None
            raise
    
    def get_embedding(self, image: Union[np.ndarray, str, bytes]) -> np.ndarray:
        """
        Generate an embedding vector for the provided image.
        
        Args:
            image: The image to embed, can be a numpy array (OpenCV format),
                  a file path, or a base64-encoded string
                  
        Returns:
            A numpy array containing the embedding vector
        """
        if self.model is None or self.processor is None:
            logger.error("Model not initialized. Using fallback random embedding.")
            return np.random.randn(self.dimensions).astype(np.float32)
        
        pil_image = self._prepare_image(image)
        
        try:
            import torch
            
            if self.model_name == "clip":
                inputs = self.processor(images=pil_image, return_tensors="pt")
                
                with torch.no_grad():
                    image_features = self.model.get_image_features(**inputs)
                
                image_embedding = image_features / image_features.norm(dim=1, keepdim=True)
                embedding = image_embedding.numpy()[0]
                
            elif self.model_name == "resnet":
                inputs = self.processor(images=pil_image, return_tensors="pt")
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                
                # Get the [CLS] token embedding
                embedding = outputs.last_hidden_state[:, 0, :].numpy()[0]
            else:
                logger.warning(f"Unsupported model: {self.model_name}. Using random embedding.")
                embedding = np.random.randn(self.dimensions).astype(np.float32)
            
            # Normalize and ensure correct dimensions
            embedding = embedding / np.linalg.norm(embedding)
            
            logger.debug(f"Generated embedding with shape {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return np.random.randn(self.dimensions).astype(np.float32)
            
    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding vector for the provided text.
        
        Args:
            text: The text to embed
                  
        Returns:
            A numpy array containing the embedding vector
        """
        if self.model is None or self.processor is None:
            logger.error("Model not initialized. Using fallback random embedding.")
            return np.random.randn(self.dimensions).astype(np.float32)
        
        if self.model_name != "clip":
            logger.warning(f"Text embeddings are only supported with CLIP model, not {self.model_name}. Using random embedding.")
            return np.random.randn(self.dimensions).astype(np.float32)
        
        try:
            import torch
            
            inputs = self.processor(text=[text], return_tensors="pt", padding=True)
            
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
            
            # Normalize the features
            text_embedding = text_features / text_features.norm(dim=1, keepdim=True)
            embedding = text_embedding.numpy()[0]
            
            logger.debug(f"Generated text embedding with shape {embedding.shape} for text: '{text}'")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating text embedding: {e}")
            return np.random.randn(self.dimensions).astype(np.float32)
    
    def _prepare_image(self, image: Union[np.ndarray, str, bytes]) -> Image.Image:
        """
        Convert the input image to PIL format required by the models.
        
        Args:
            image: Input image in various formats
            
        Returns:
            PIL Image object
        """
        if isinstance(image, np.ndarray):
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            return Image.fromarray(image_rgb)
            
        elif isinstance(image, str):
            if os.path.isfile(image):
                return Image.open(image)
            else:
                try:
                    image_data = base64.b64decode(image)
                    return Image.open(io.BytesIO(image_data))
                except Exception as e:
                    logger.error(f"Failed to decode image string: {e}")
                    raise ValueError("Invalid image string format")
                
        elif isinstance(image, bytes):
            return Image.open(io.BytesIO(image))
            
        else:
            raise ValueError(f"Unsupported image format: {type(image)}")
