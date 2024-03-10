from PIL import Image


file_path = 'map.txt'
image_path = 'map.png'


def write_binary_data_to_file(file_path, data_array):
    try:
        with open(file_path, 'w') as file:
            # Convert the list of 1s and 0s to a string and write it to the file
            data_str = ''.join(map(str, data_array))
            file.write(data_str)
        print(f"Data successfully written to {file_path}")
    except Exception as e:
        print(f"Error writing data to {file_path}: {e}")


def convert_image_to_binary(image_path):
    try:
        # Open the image
        img = Image.open(image_path)

        # Convert the image to grayscale
        gray_img = img.convert('L')

        # Get the pixel data as a list of lists
        pixels = list(gray_img.getdata())
        width, height = gray_img.size
        pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]

        # Convert to binary representation
        binary_map = [[0 if pixel >= 200 else 1 for pixel in row]
                      for row in pixels]

        return binary_map
    except Exception as e:
        print(f"Error converting image to binary: {e}")
        return None


def create_image_from_binary(binary_map, output_path='output_image.png'):
    try:
        # Convert binary values to 0 (black) and 255 (white)
        pixels = [[0 if value == 1 else 255 for value in row]
                  for row in binary_map]

        # Convert the 2D list to a flat list
        flat_pixels = [pixel for row in pixels for pixel in row]

        # Get the dimensions of the binary map
        width = len(binary_map[0])
        print(width)
        height = len(binary_map)

        # Create a new image with the given pixel values
        img = Image.new('L', (width, height))
        img.putdata(flat_pixels)

        # Save the image
        img.save(output_path)
        print(f"Image saved to {output_path}")
    except Exception as e:
        print(f"Error creating image from binary map: {e}")


binary_map = convert_image_to_binary(image_path)
create_image_from_binary(binary_map, output_path='output_image.png')

data_array = []
for y in range(len(binary_map)):
    for x in range(len(binary_map[y])):
        if binary_map[y][x] == 1:
            if y % 2 == 0:
                if x % 2 == 0:
                    data_array.append(1)
                else:
                    data_array.append(2)
            else:
                if x % 2 == 0:
                    data_array.append(2)
                else:
                    data_array.append(1)
        else:
            data_array.append(0)
write_binary_data_to_file(file_path, data_array)



