from keras.models import load_model
from keras.preprocessing.image import img_to_array
import numpy as np
from PIL import Image
from skimage.transform import resize

# Input is an image-CNN runs prediction on image-Returns image prediction as a list of float(s)
'''
function to restore CNN and run prediction on a particular image

input: 

output:
- result - list of floats that represents the classification (~0 for abnormal, ~1 for echolocation)
'''
model = ' '

def classifyCNN(file_name):
    image = Image.open(file_name)

    # load CNN model for predictions
    if model == ' ':
        model = load_model('CNN200x300ep30.h5')

    # change image dimensions to desired values for resizing
    image_height, image_width = 200, 300

    # resize image for desired CNN model
    image_resize = image.resize((image_width, image_height))

    '''# convert image to an array
    imagearray = img_to_array(image_resize)

    # add 4th dimension to array for CNN -> will get error otherwise
    imagearray=np.expand_dims(imagearray, 0)
    
    # convert array so that its predictions are readable
    imagearray /= 255'''

    # convert image to array and add 4th dimension
    image_array = np.expand_dims(img_to_array(image_resize), 0)

    # rescale image array (have values b/t 0 and 1)
    image_array /= 255

    # run prediction on image and obtain list of float predictions
    prediction = model.predict(image_array)

    # extract the prediction float from element 0
    result = prediction[0]

    # TODO: if-statement cutoff: 0 for less than 0.9, 1 otherwise
    result = (result < 0.9) ? 0 : 1

    # return value is a float that represents the classification: ~0 = abnormal,~1 = echolocation
    return result
