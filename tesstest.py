import pytesseract
from PIL import Image, ImageOps

# image = Image.open("test_images/handwritten_sample_easy.png")
# image = Image.open("test_images/printed_sample.png")
image = Image.open("test_images/10 random aresses PNG/page-10.png")

# processing for better accuracy
# image = image.crop((280, 50, 800, 1050))
# image = image.rotate(-90, expand=True)
image = ImageOps.grayscale(image)
image = image.resize((image.width * 3, image.height * 3))
image = ImageOps.autocontrast(image)
image = image.point(lambda p: 255 if p > 160 else 0)

# check how the image looks
image.save("output_image/debug_output.png")

# convertion
text = pytesseract.image_to_string(image)
print(repr(text))
