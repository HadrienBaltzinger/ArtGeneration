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
    """ Définit les dimensions de l'image cible

    La longueur sera toujours de 400 pixels
    La largeur est définie proportionellement pour ne pas déformer l'image

    params : 
        content_image_path (string): chemin vers l'image de contenu
    
    returns :
        img_nrows : longueur cible de l'image
        img_ncols : largeur cible de l'image 
    """
    width, height = keras.preprocessing.image.load_img(content_image_path).size
    img_nrows = 400
    img_ncols = int(width * img_nrows / height)
    return img_nrows, img_ncols


def preprocess_image(image_path, target_size):
    """Fonction qui ouvre, resize et formate une image

    params :
        image_path (string) : chemin vers l'image 
        target_size (int, int) : dimensions de l'image cible

    returns :
        l'image formatée dans un tenseur
    """
    img = keras.preprocessing.image.load_img(
        image_path, target_size=target_size
    )
    img = keras.preprocessing.image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = vgg19.preprocess_input(img)
    return tf.convert_to_tensor(img)


def deprocess_image(x, target_size):
    """Fonction qui transforme une image tensorisée
        en une image valide

    params :
        x (tf.tensor) : image tensorisée 
        target_size (int, int) : dimensions de l'image cible

    returns :
        l'image dans un np.array
    """
    x = x.reshape((*target_size, 3))
    # Remove zero-center by mean pixel
    x[:, :, 0] += 103.939
    x[:, :, 1] += 116.779
    x[:, :, 2] += 123.68
    # transforme encodage BGR en RGB
    x = x[:, :, ::-1]
    x = np.clip(x, 0, 255).astype("uint8")
    return x



### --- Fonctions de perte ---
def gram_matrix(x):
    """Fonction qui calcule la Matrice de gram d'une image

    params :
        x (tf.tensor) : image tensorisée 

    returns :
        np.array, la matrice de gram
    """
    x = tf.transpose(x, (2, 0, 1))
    features = tf.reshape(x, (tf.shape(x)[0], -1))
    gram = tf.matmul(features, tf.transpose(features))
    return gram


def style_loss(style, result, target_size):
    """Calcule la fonction de perte de style

    Evalue la conservation du style entre l'image de style et l'image résultat

    params :
        style (tf.tensor) : image de style tensorisée 
        result (tf.tensor) : image resultat tensorisée
        target_size (int, int) : dimensions de l'image cible

    returns :
        float, une évaluation de la conservation du style
    """
    S = gram_matrix(style)
    C = gram_matrix(result)
    channels = 3
    size = target_size[0]*target_size[1]
    return tf.reduce_sum(tf.square(S - C)) / (4.0 * (channels ** 2) * (size ** 2))


def content_loss(content, result):
    """Calcule la fonction de perte de contenu

    Evalue la conservation du contenu entre l'image de contenu et l'image résultat

    params :
        content (tf.tensor) : image de contenu tensorisée 
        result (tf.tensor) : image resultat tensorisée

    returns :
        float, une évaluation de la conservation du contenu
    """
    return tf.reduce_sum(tf.square(result - content))


def total_variation_loss(x, target_size):
    """Calcule la fonction de perte de cohérence locale

    Evalue la cohérence locale de l'image générée

    params :
        x (tf.tensor) : image resultat tensorisée
        target_size (int, int) : dimensions de l'image cible

    returns :
        float, une évaluation de la cohérence locale de l'image
    """
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
    """ Classe correspondant à un modèle de transfert de style """

    def __init__(self, content_path, style_path, result_path, weights=(2.5e-8, 1e-6, 1e-6)):
        """ Initialisation de la classe

        params :
            content_path (string): chemin vers l'image source de contenu
            style_path (string): chemin vers l'image source de style
            result_path (string): chemin où sauvegarder l'image resultat
            weights (float, float, float): poids à appliquer aux différentes losses
        """
        self.target_size = get_dim(content_path)
        self.content_image = preprocess_image(content_path, self.target_size)
        self.style_image = preprocess_image(style_path, self.target_size)
        self.result_image = tf.Variable(self.content_image)
        self.result_path = result_path
        self.weights = weights
        self.build_model()
        self.set_losses_layers()
    
    def build_model(self):
        """ Charge le modèle (VGG19) pré-entrainé sur ImageNet """
        model = vgg19.VGG19(weights="imagenet", include_top=False)
        # sortie de chaque couche du réseau
        outputs_dict = dict([(layer.name, layer.output) for layer in model.layers])
        # modele qui retourne les valeurs d'activation de chaque couche du réseau
        self.feature_extractor = keras.Model(inputs=model.inputs, outputs=outputs_dict)

    def set_losses_layers(self):
        """ Définir les couches utilisées pour les deux fonctions de perte
            * style_loss
            * content_loss
        """
        self.style_layer_names = [
            "block1_conv1",
            "block2_conv1",
            "block3_conv1",
            "block4_conv1",
            "block5_conv1",
        ]
        self.content_layer_name = "block5_conv2"
    
    
    def compute_loss(self):
        """ Calcule les valeurs des 3 fonctions de pertes
        Et en déduit la perte globale du réseau
        """
        content_weight, style_weight, total_variation_weight = self.weights
        input_tensor = tf.concat(
            [self.content_image, self.style_image, self.result_image], axis=0
        )
        features = self.feature_extractor(input_tensor)

        # initialisation
        loss = tf.zeros(shape=())

        # content_loss
        layer_features = features[self.content_layer_name]
        content_image_features = layer_features[0, :, :, :]
        combination_features = layer_features[2, :, :, :]
        loss = loss + content_weight * content_loss(
            content_image_features, combination_features
        )
        # style_loss
        for layer_name in self.style_layer_names:
            layer_features = features[layer_name]
            style_reference_features = layer_features[1, :, :, :]
            combination_features = layer_features[2, :, :, :]
            sl = style_loss(style_reference_features, combination_features, self.target_size)
            loss += (style_weight / len(self.style_layer_names)) * sl

        # total_variation_loss
        loss += total_variation_weight * total_variation_loss(self.result_image, self.target_size)
        return loss

    @tf.function
    def compute_loss_and_grads(self):
        """ Calcule les pertes et les gradients

        tf.function pour gagner en efficacité de calcul
        """
        with tf.GradientTape() as tape:
            loss = self.compute_loss()
        grads = tape.gradient(loss, self.result_image)
        return loss, grads
    
    def train(self, optimizer, epochs, verbose=False):
        """ Entrainement du réseau sur les images données

        L'image resultat est sauvegardée à l'adresse définie plus tot

        params:
            optimizer : optimiseur
            epochs : nombre d'epochs d'entrainement
            verbose : indique s'il faut afficher les détails de l'entrainement
        return:
            history : l'historique de variation de la loss au cours de l'entrainement
        """
        history = []

        for i in range(1, epochs + 1):
            loss, grads = self.compute_loss_and_grads()
            optimizer.apply_gradients([(grads, self.result_image)])
            # enregistrement de la loss
            history.append(loss)
            if verbose:
                print("Iteration %d: loss=%.2f" % (i, loss))
        # fin de l'entrainement
        print("--- \nFin de l'entrainemnt : loss finale = %.2f"%loss)
        # enregistrement de l'image résultat
        img = deprocess_image(self.result_image.numpy(), self.target_size)
        keras.preprocessing.image.save_img(self.result_path, img)
        return history



### --- fonction principale ---
def apply_style(content_path, style_path, result_path, epochs=10, weights=(2.5e-8, 1e-6, 1e-6)):
    """ Fonction principale : effectue le transfert de style d'une image à l'autre

    params :
        content_path (string): chemin vers l'image source de contenu
        style_path (string): chemin vers l'image source de style
        result_path (string): chemin où sauvegarder l'image resultat
        epochs (int): nombre d'epochs de l'entrainement
        weights (float, float, float): poids à appliquer aux différentes losses
            * total_variation_weight = 1e-6
            * style_weight = 1e-6
            * content_weight = 2.5e-8
    """    
    
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
      verbose=False
      )
    
    print("Exécution terminée ... Temps de traitement : %s seconds" % (time.time() - start_time))


content = "/home/eisti/Desktop/ING3/PFE/ArtGeneration/Data/test/Photo/0a7b607c9c.jpg"
style = "/home/eisti/Desktop/ING3/PFE/ArtGeneration/Data/test/Symbolism/nicholas-roerich_message-from-shambhala-arrow-letter-1946.jpg"
result = "/home/eisti/Desktop/ING3/PFE/ArtGeneration/Data/result/test3.jpg"
apply_style(content, style, result, epochs=10)