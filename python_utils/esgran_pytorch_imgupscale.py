#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: upscale_with_esrgan_gpu.py
Date: 2024-10-22
Author: [Your Name]
Purpose: Batch upscale images in a folder using ESRGAN with GPU support via PyTorch (CUDA).
Inputs:
    - input_dir: Directory containing the images to be upscaled (.jpg, .jpeg, .png).
    - output_dir: Directory where the upscaled images will be saved.
    - esrgan_model: Pre-trained ESRGAN PyTorch model to use for upscaling.
Outputs:
    - AI-upscaled images saved to the specified output directory.
Requirements:
    - PyTorch with GPU support (CUDA)
    - ESRGAN model file (PyTorch format)
    - Pillow (PIL) for image handling: `pip install Pillow`
Description:
    This script utilizes GPU acceleration for batch upscaling images with the ESRGAN model.
"""

import os
import torch
from PIL import Image
import torchvision.transforms as transforms

class ESRGANUpscaler:
    """
    Class to handle AI-based image upscaling using ESRGAN with PyTorch for GPU acceleration.
    It processes all images in the specified input directory and saves them to the output directory.
    """

    def __init__(self, input_dir, output_dir, esrgan_model):
        """
        Initializes the ESRGANUpscaler with paths to the input and output directories and the ESRGAN model.
        
        Args:
            input_dir (str): Path to the folder containing images to upscale.
            output_dir (str): Path to the folder where upscaled images will be saved.
            esrgan_model (str): Path to the pre-trained ESRGAN model in PyTorch format.
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load ESRGAN model
        self.model = torch.load(esrgan_model, map_location=self.device)
        self.model.eval()

        # Create the output directory if it does not exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def upscale_images(self):
        """
        Upscales all images in the input directory using the ESRGAN model.
        Saves the upscaled images to the output directory.
        """
        # Define transformation to convert images to tensors and back
        transform_to_tensor = transforms.ToTensor()
        transform_to_image = transforms.ToPILImage()

        # Iterate over each image file in the input directory
        for img_file in os.listdir(self.input_dir):
            # Check if the file is an image (supports .jpg, .jpeg, .png formats)
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                input_path = os.path.join(self.input_dir, img_file)
                output_path = os.path.join(self.output_dir, img_file)

                # Open the image using Pillow (PIL)
                img = Image.open(input_path).convert('RGB')

                # Convert image to tensor and move to GPU
                img_tensor = transform_to_tensor(img).unsqueeze(0).to(self.device)

                # Perform upscaling using the ESRGAN model on the GPU
                with torch.no_grad():
                    print(f"Upscaling {img_file} using ESRGAN on {self.device}...")
                    upscaled_tensor = self.model(img_tensor)

                # Convert tensor back to an image
                upscaled_img = transform_to_image(upscaled_tensor.squeeze(0).cpu())

                # Save the upscaled image to the output directory
                upscaled_img.save(output_path)
                print(f"Saved upscaled image: {output_path}")

if __name__ == "__main__":
    # Define the paths for input, output, and ESRGAN model
    input_directory = "C:/path/to/input_images"
    output_directory = "C:/path/to/output_images"
    esrgan_model_path = "C:/path/to/esrgan_model.pth"

    # Instantiate the upscaler class
    upscaler = ESRGANUpscaler(input_directory, output_directory, esrgan_model_path)

    # Start the image upscaling process
    upscaler.upscale_images()
