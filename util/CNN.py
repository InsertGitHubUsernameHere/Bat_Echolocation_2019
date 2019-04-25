from keras.preprocessing.image import img_to_array
import numpy as np
from PIL import Image

# Input is an image-CNN runs prediction on image-Returns image prediction as a list of float(s)
'''
function to restore CNN and run prediction on a particular image

input: 

output:
- result - list of floats that represents the classification (~0 for abnormal, ~1 for echolocation)
'''


def classifyCNN(file_name, model):
    image = Image.open(file_name)

    # change image dimensions to desired values for resizing
    image_height, image_width = 200, 300

    # resize image for desired CNN model
    image_resize = image.resize((image_width, image_height)).convert('RGB')

    # convert image to array and add 4th dimension
    image_array = img_to_array(image_resize)

    image_array = np.expand_dims(image_array, 0)

    # rescale image array (have values b/t 0 and 1)
    image_array /= 255

    # run prediction on image and obtain list of float predictions
    prediction = model.predict(image_array)

    # extract the prediction float from element 0
    result = prediction[0]

    # TODO: if-statement cutoff: 0 for less than 0.9, 1 otherwise
    result = 0 if result < 0.5 else 1

    # return value is a float that represents the classification: ~0 = abnormal,~1 = echolocation
    return result
