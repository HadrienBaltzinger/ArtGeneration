import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from skimage.io import imread
import pandas as pd

file_path = "../Data/base-joconde-extrait.csv"
# lecture du fichier
data = pd.read_csv(file_path, sep=";", quotechar="\"")
# print(data.head())
# selection des données de domaines correspondant à nos recherches (peintures et dessins)
data = data[(data.Domaine.str.contains("peinture")) | (data.Domaine.str.contains("dessin"))]
# suppression les lignes sans titre
data = data[(data.Titre.str.contains("Sans titre") == False) & (data["Titre"].isnull() == False)]
# selection de la liste des titres
titres = data.Titre
# enregistrement dans un nouveau fichier
df = pd.DataFrame(titres)
df.to_csv("../Data/title_data.txt", index = None)