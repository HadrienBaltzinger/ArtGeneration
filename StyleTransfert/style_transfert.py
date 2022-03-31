import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import vgg19
import matplotlib.pyplot as plt
from skimage.io import imread
from IPython.display import Image, display
import time



### --- Fonctions utiles / processing des images ---
def get_dim(content_image_path):
  # Récupère les dimensions de l'image cible (longueur set et largeur proportionnelle)
  width, height = keras.preprocessing.image.load_img(content_image_path).size
  img_nrows = 400
  img_ncols = int(width * img_nrows / height)
  return img_nrows, img_ncols


def preprocess_image(image_path, target_size):
    # Util function to open, resize and format pictures into appropriate tensors
    img = keras.preprocessing.image.load_img(
        image_path, target_size=target_size
    )
    img = keras.preprocessing.image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = vgg19.preprocess_input(img)
    return tf.convert_to_tensor(img)


def deprocess_image(x, target_size):
    # Util function to convert a tensor into a valid image
    x = x.reshape((*target_size, 3))
    # Remove zero-center by mean pixel
    x[:, :, 0] += 103.939
    x[:, :, 1] += 116.779
    x[:, :, 2] += 123.68
    # 'BGR'->'RGB'
    x = x[:, :, ::-1]
    x = np.clip(x, 0, 255).astype("uint8")
    return x



### --- Fonctions de perte ---
# The gram matrix of an image tensor (feature-wise outer product)
def gram_matrix(x):
    x = tf.transpose(x, (2, 0, 1))
    features = tf.reshape(x, (tf.shape(x)[0], -1))
    gram = tf.matmul(features, tf.transpose(features))
    return gram

# The "style loss" is designed to maintain
# the style of the reference image in the generated image.
# It is based on the gram matrices (which capture style) of
# feature maps from the style reference image
# and from the generated image
def style_loss(style, result, target_size):
    S = gram_matrix(style)
    C = gram_matrix(result)
    channels = 3
    size = target_size[0]*target_size[1]
    return tf.reduce_sum(tf.square(S - C)) / (4.0 * (channels ** 2) * (size ** 2))

# An auxiliary loss function
# designed to maintain the "content" of the
# base image in the generated image
def content_loss(content, result):
    return tf.reduce_sum(tf.square(result - content))

# The 3rd loss function, total variation loss,
# designed to keep the generated image locally coherent
def total_variation_loss(x, target_size):
  nrows, ncols = target_size
  a = tf.square(
    x[:, : nrows - 1, : ncols - 1, :] - x[:, 1:, : ncols - 1, :]
  )
  b = tf.square(
    x[:, : nrows - 1, : ncols - 1, :] - x[:, : nrows - 1, 1:, :]
  )
  return tf.reduce_sum(tf.pow(a + b, 1.25))



### --- Création du modèle ---
class StyleTransfertModel():
    def __init__(self, content_path, style_path, result_path, weights):
        self.target_size = get_dim(content_path)
        self.content_image = preprocess_image(content_path, self.target_size)
        self.style_image = preprocess_image(style_path, self.target_size)
        self.result_image = tf.Variable(self.content_image)
        self.result_path = result_path
        self.weights = weights
        self.build_model()
        self.set_losses_layers()
    
    def build_model(self):
        # Build a VGG19 model loaded with pre-trained ImageNet weights
        model = vgg19.VGG19(weights="imagenet", include_top=False)
        # Get the symbolic outputs of each "key" layer (we gave them unique names).
        outputs_dict = dict([(layer.name, layer.output) for layer in model.layers])
        # Set up a model that returns the activation values for every layer in VGG19 (as a dict).
        self.feature_extractor = keras.Model(inputs=model.inputs, outputs=outputs_dict)

    def set_losses_layers(self):
        # List of layers to use for the style loss.
        self.style_layer_names = [
            "block1_conv1",
            "block2_conv1",
            "block3_conv1",
            "block4_conv1",
            "block5_conv1",
        ]
        # The layer to use for the content loss.
        self.content_layer_name = "block5_conv2"
    

    def compute_loss(self):
        content_weight, style_weight, total_variation_weight = self.weights
        input_tensor = tf.concat(
            [self.content_image, self.style_image, self.result_image], axis=0
        )
        features = self.feature_extractor(input_tensor)

        # Initialize the loss
        loss = tf.zeros(shape=())

        # Add content loss
        layer_features = features[self.content_layer_name]
        content_image_features = layer_features[0, :, :, :]
        combination_features = layer_features[2, :, :, :]
        loss = loss + content_weight * content_loss(
            content_image_features, combination_features
        )
        # Add style loss
        for layer_name in self.style_layer_names:
            layer_features = features[layer_name]
            style_reference_features = layer_features[1, :, :, :]
            combination_features = layer_features[2, :, :, :]
            sl = style_loss(style_reference_features, combination_features, self.target_size)
            loss += (style_weight / len(self.style_layer_names)) * sl

        # Add total variation loss
        loss += total_variation_weight * total_variation_loss(self.result_image, self.target_size)
        return loss

    # @tf.function
    def compute_loss_and_grads(self):
        with tf.GradientTape() as tape:
            loss = self.compute_loss()
        grads = tape.gradient(loss, self.result_image)
        return loss, grads
    
    def train(self, optimizer, epochs, nb_saves=0, verbose=False):
        """ entrainement du réseau sur les images données

        params:
            content_image : image dont le contenu sera utilisé
            style_image : image dont le style sera utilisé
            result_path : chemin où sauvegarder les résultats successifs
            result_image : contient
            nb_saves : nombre de sauvegardes d'images à faire au long de l'entrainement
            verbose : indique s'il faut afficher les détails de l'entrainement
        """

        save_rate = int(epochs/nb_saves) if nb_saves !=0 else epochs
        history = []

        for i in range(1, epochs + 1):
            loss, grads = self.compute_loss_and_grads()
            optimizer.apply_gradients([(grads, self.result_image)])
            # enregistrement de la loss
            history.append(loss)
            if i % save_rate == 0:
                if verbose:
                    print("Iteration %d: loss=%.2f" % (i, loss))
                # img = deprocess_image(self.result_image.numpy(), self.target_size)
                # fname = self.result_path #+ "_at_iteration_%d.png" % i
                # keras.preprocessing.image.save_img(fname, img)
        # fin de l'entrainement
        print("--- \nFin de l'entrainemnt : loss finale = %.2f"%loss)
        # enregistrement de l'image résultat
        img = deprocess_image(self.result_image.numpy(), self.target_size)
        keras.preprocessing.image.save_img(self.result_path, img)
        return history



### --- fonction principale ---
def apply_style(content_path, style_path, result_path, epochs=50, weights=(2.5e-8, 1e-6, 1e-6)):
    # Poids des composants de la loss (à optimiser)
    # total_variation_weight = 1e-6
    # style_weight = 1e-6
    # content_weight = 2.5e-8
    # weights = (content_weight, style_weight, total_variation_weight)

    start_time = time.time()
    optimizer = keras.optimizers.SGD(
        keras.optimizers.schedules.ExponentialDecay(
            initial_learning_rate=100.0, decay_steps=100, decay_rate=0.96
        )
    )

    model = StyleTransfertModel(content_path, style_path, result_path, weights)
    model.train(
      optimizer, 
      epochs, 
      nb_saves=0, 
      verbose=False
      )
    
    print("Exécution terminée ... Temps de traitement : %s seconds" % (time.time() - start_time))


content = "/home/eisti/Desktop/ING3/PFE/ArtGeneration/Data/test/Photo/0a7b607c9c.jpg"
style = "/home/eisti/Desktop/ING3/PFE/ArtGeneration/Data/test/Symbolism/nicholas-roerich_message-from-shambhala-arrow-letter-1946.jpg"
result = "/home/eisti/Desktop/ING3/PFE/ArtGeneration/Data/result/test3.jpg"
apply_style(content, style, result, epochs=10, weights=(2.5e-8, 1e-6, 1e-6))