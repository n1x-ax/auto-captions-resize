# Image Captioning and Resizing for LoRA Training

## Overview
This script helps you prepare datasets for training LoRA (Low-Rank Adaptation) models and other image models. It processes images from a specified input folder, generates captions using OpenAI's API, and creates a grid image that shows the processed images along with their captions. This is useful for creating quality training data.

## Requirements
- Python 3.x
- Pillow library (`pip install Pillow`)
- OpenAI library (`pip install openai`)

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/n1x-ax/auto-captions-resize
   cd auto-captions-resize
   ```

2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Replace `YOUR_API_KEY` in `main.py` with your actual OpenAI API key.

## Usage
1. Put your images in the `./input/` directory. Supported formats are PNG, JPG, and JPEG. Make sure the images are what you want to train your model on.

2. Run the script:
   ```bash
   python main.py
   ```

3. The processed images and their captions will be saved in the `output_folder` directory. You'll also get a grid image named `image_grid.jpg` that gives you a quick look at your dataset.

## Features

### 1. Image Resizing
- The script resizes images to 512x512 pixels for consistent input dimensions, which helps with model training.
- If an image is square, it gets resized to 768x768 pixels to keep more detail. Non-square images are center-cropped to a square before resizing.
- Images smaller than 512 pixels in either dimension are resized directly to 512x512 pixels.

### 2. Auto-Captioning
- The script uses OpenAI's API to generate captions for each image. These captions start with a relevant artistic trigger word and end with an artistic style descriptor, which can be helpful for training.
- Captions are saved in text files for easy access.

## Functions
- `encode_image(image_path)`: Converts an image to Base64 format for API usage.
- `create_captions_for_images(input_folder, output_folder, rescale_images=True)`: Processes images, generates captions, and saves them.
- `create_image_grid_with_captions(output_folder, grid_image_path)`: Creates a grid image with captions from the processed images.

## License
This script is shared under the MIT License. See the [LICENSE](LICENSE) file for details.
