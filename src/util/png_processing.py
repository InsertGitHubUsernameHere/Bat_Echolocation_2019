# function to encode png image from file_path into byte data
def encode_png_to_blob(file_path):
    with open(file_path, 'rb') as img:
        file = img.read()
        byte_array = bytearray(file)

    # print(byte_array)
    return byte_array


# function to create and write into a new png file "img_name.png" from obtained byte data
def decode_blob_to_png(img_name, byte_array):
    file = open('{}'.format(img_name), 'wb+')
    file.write(byte_array)
    file.close()
