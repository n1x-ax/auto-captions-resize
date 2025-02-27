import os
import base64
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI

# Initialize OpenAI client with your API key
client = OpenAI(api_key='YOUR_API_KEY')

# Function to encode the image to Base64 format
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function to create captions for images in a specified folder
def create_captions_for_images(input_folder, output_folder, rescale_images=True):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all image files in the input folder
    image_files = [f for f in os.listdir(input_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

    # Process each image file
    for index, image_file in enumerate(image_files, start=1):
        # Open the image
        with Image.open(os.path.join(input_folder, image_file)) as img:
            # Rescale images if the flag is set
            if rescale_images:
                # Check if the image is square
                if img.width == img.height:
                    resized_img = img.resize((768, 768))  # Resize square images
                else:
                    # Calculate the center crop box for non-square images
                    min_side = min(img.width, img.height)
                    left = (img.width - min_side) / 2
                    top = (img.height - min_side) / 2
                    right = (img.width + min_side) / 2
                    bottom = (img.height + min_side) / 2

                    # Crop the image to a square
                    cropped_img = img.crop((left, top, right, bottom))
                    
                    # Resize the cropped image to 512x512
                    resized_img = cropped_img.resize((512, 512))

                # Resize smaller images directly to 512x512
                if img.width < 512 or img.height < 512:
                    resized_img = img.resize((512, 512))
            else:
                resized_img = img  # Use original image if no rescaling

            # Convert image to 'RGB' if it has an alpha channel
            if resized_img.mode == 'RGBA':
                resized_img = resized_img.convert('RGB')
            
            # Save the resized image with a new name
            image_name = f"image{index}.jpg"
            resized_img.save(os.path.join(output_folder, image_name))
            
            # Encode the image in Base64 for OpenAI API
            base64_image = encode_image(os.path.join(output_folder, image_name))

            # Generate caption using the OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": "Analyze this image and provide a single, detailed sentence. Begin with a relevant artistic TRIGGER WORD (e.g., 'Photograph', 'Digital Art', 'Illustration', etc.). Describe the main subject, key visual elements, composition, and notable details. End the sentence with ', [ARTISTIC STYLE] style' where [ARTISTIC STYLE] best matches the image's aesthetic (e.g., 'minimalist', 'vintage', 'contemporary', etc.)."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )

            # Print the response to understand its structure
            print(response)

            # Access the content based on the actual structure
            caption = response.choices[0].message.content.strip()

            # Save the caption to a text file
            with open(os.path.join(output_folder, f"image{index}.txt"), 'w') as text_file:
                text_file.write(caption)

# Function to create a grid image with captions
def create_image_grid_with_captions(output_folder, grid_image_path):
    # Load all images and captions
    image_files = sorted([f for f in os.listdir(output_folder) if f.endswith('.jpg')])
    captions = []
    for index in range(1, len(image_files) + 1):
        with open(os.path.join(output_folder, f"image{index}.txt"), 'r') as text_file:
            captions.append(text_file.read().strip())

    # Determine grid size based on the number of images
    num_images = len(image_files)
    grid_cols = int(num_images**0.5)  # Calculate number of columns
    grid_rows = (num_images + grid_cols - 1) // grid_cols  # Calculate number of rows
    image_size = 512
    caption_height = 100  # Increased height for better text wrapping

    # Create a new image for the grid
    grid_image = Image.new('RGB', (grid_cols * image_size, grid_rows * (image_size + caption_height)), (255, 255, 255))
    draw = ImageDraw.Draw(grid_image)

    # Load a font for captions
    try:
        font = ImageFont.truetype("arial.ttf", 16)  # Reduced font size for better fit
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font if arial is not available

    # Function to wrap text for captions
    def wrap_text(text, font, max_width):
        lines = []
        words = text.split()
        while words:
            line = ''
            while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
                line += (words.pop(0) + ' ')
            lines.append(line)
        return lines

    # Place images and captions in the grid
    for i, (image_file, caption) in enumerate(zip(image_files, captions)):
        img = Image.open(os.path.join(output_folder, image_file))
        x = (i % grid_cols) * image_size  # Calculate x position
        y = (i // grid_cols) * (image_size + caption_height)  # Calculate y position
        grid_image.paste(img, (x, y))  # Paste image in grid

        # Draw the caption below the image
        wrapped_text = wrap_text(caption, font, image_size - 20)
        for j, line in enumerate(wrapped_text):
            draw.text((x + 10, y + image_size + 10 + j * 20), line, fill="black", font=font)

    # Save the grid image to the specified path
    grid_image.save(grid_image_path)

# Main execution block
if __name__ == "__main__":
    input_folder = './input/'  # Input folder containing images
    output_folder = os.path.join(os.getcwd(), 'output_folder')  # Output folder for processed images and captions
    create_captions_for_images(input_folder, output_folder, rescale_images=False)  # Set to False to skip rescaling
    create_image_grid_with_captions(output_folder, os.path.join(output_folder, 'image_grid.jpg'))  # Create grid image