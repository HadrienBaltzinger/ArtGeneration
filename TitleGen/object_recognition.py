import tensorflow as tf
from tensorflow import keras
import numpy as np
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from translate import Translator
import matplotlib.pyplot as plt
import cv2


model = tf.keras.applications.ResNet50(include_top=True, weights='imagenet')

# fonction effectuant l'analyse
def detect(img_path):
    """ Detecte 3 objets dans une image donnée
    
    params :
        img_path (string) : chemin de l'image
    """
    img = plt.imread(img_path)

    img = cv2.resize(img, (224,224)).astype("float32")
    img_batch = preprocess_input(img[np.newaxis]) 

    predictions = model.predict(img_batch)
    labels = decode_predictions(predictions)

    translator= Translator(from_lang="english",to_lang="french")
    keywords = [translator.translate(l[1].replace("_", " ")) for l in labels[0][:3]]
    probas = [l[2] for l in labels[0][:3]]

    return keywords, probas

print(detect("Data/wikiart-base/Symbolism/frantisek-kupka_ballad-of-epona-1900.jpg"))