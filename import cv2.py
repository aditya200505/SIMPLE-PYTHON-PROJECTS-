import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Characters sorted from densest to lightest.
# Dark areas get '@', bright areas get '.'
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

# The size of the font and the grid spacing.
# Increase this number for faster performance but lower resolution.
FONT_SIZE = 10 

# Load the font once to improve performance
try:
    # 'consola.ttf' is a monospace font on Windows, better for ASCII alignment.
    FONT = ImageFont.truetype("consola.ttf", FONT_SIZE)
except IOError:
    FONT = ImageFont.load_default()

# ---------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------

def frame_to_ascii_overlay(frame):
    """
    Takes an OpenCV frame, converts it to PIL, draws ASCII characters
    based on brightness, and converts it back to OpenCV format.
    """
    
    # 1. Convert OpenCV frame (BGR) to PIL Image (RGB)
    # OpenCV uses BGR colors, but Pillow uses RGB.
    cv2_im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im_rgb)

    # Create a white background image so the original face is not visible
    output_im = Image.new("RGB", pil_im.size, (255, 255, 255))

    # 2. Create a drawing object to draw text on the image
    draw = ImageDraw.Draw(output_im)

    # 4. Convert the image to grayscale to calculate brightness easily
    # We don't display this, we just use it for math.
    gray_im = pil_im.convert("L")
    
    # Get image dimensions
    width, height = pil_im.size

    # 5. Loop through the image in a grid (steps of FONT_SIZE)
    for y in range(0, height, FONT_SIZE):
        for x in range(0, width, FONT_SIZE):
            
            # Get the brightness of the pixel at the current grid position (x, y)
            # (0 is black, 255 is white)
            brightness = gray_im.getpixel((x, y))
            
            # 6. Map brightness to an ASCII character
            # We have len(ASCII_CHARS) characters.
            # We map the 0-255 brightness range to the 0-10 index range.
            char_index = int((brightness / 255) * (len(ASCII_CHARS) - 1))
            
            # Select the character
            ascii_char = ASCII_CHARS[char_index]

            # 7. Draw the character on the original color image
            # We draw in black (0, 0, 0)
            draw.text((x, y), ascii_char, font=FONT, fill=(0, 0, 0))

    # 8. Convert back to OpenCV format (RGB -> BGR) so we can display it
    processed_frame = cv2.cvtColor(np.array(output_im), cv2.COLOR_RGB2BGR)
    
    return processed_frame

def main():
    # Initialize the webcam (0 is usually the default camera)
    # To use a file instead, replace 0 with "filename.mp4" or "image.jpg"
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 'q' to quit the application.")

    while True:
        try:
            # Read a frame from the webcam
            ret, frame = cap.read()
            
            if not ret or frame is None:
                print("Failed to grab frame.")
                break

            # Resize frame for better performance (ASCII conversion is CPU intensive)
            frame = cv2.resize(frame, (640, 480))

            # Process the frame to add ASCII overlay
            output_image = frame_to_ascii_overlay(frame)

            # Display the result in a window
            cv2.imshow('ASCII Art Overlay', output_image)

            # Exit loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    # Cleanup: Release camera and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
