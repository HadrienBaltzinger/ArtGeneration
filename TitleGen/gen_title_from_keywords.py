import pandas as pd
import string
import numpy as np
import json
import tensorflow as tf
import yake
import sklearn
from keytotext import pipeline, trainer

def extraction(text):
    doublets = extractor.extract_keywords(text)
    keywords = [w for (w,_) in doublets]
    # il faut exactement le même nombre de keywords pour chaque titre
    # on rajoute des keywords vides pour avoir une liste de la bonne taille
    while len(keywords) < n_keywords_per_title:
        keywords.append(" ")
    return keywords

def train(data_file = "Data/title_data.txt", output_dir="Models/titlegen/keytotext/"):
    data = pd.read_csv(data_file)

    # PROCESSING
    data = data.rename(columns={"Titre":"text"})
    n_keywords_per_title = 3
    extractor = yake.KeywordExtractor(lan="fr", n=1, top=n_keywords_per_title)
    # data = data[:30000]
    data["keywords"] = data["text"].astype("str").apply(extraction)
    # prep train-test split
    data = sklearn.utils.shuffle(data)
    test_split = int(0.1*data.shape[0])
    test_df = data[:test_split]
    train_df = data[test_split:]

    # entrainement
    model = trainer()
    model.from_pretrained(model_name="t5-small")

    model.train(
            train_df,
            test_df,
            source_max_token_len = 90,
            target_max_token_len = 10,
            batch_size = 32,
            max_epochs = 10,
            use_gpu = True,
            outputdir=output_dir,
            early_stopping_patience_epochs = 2,  # 0 to disable early stopping feature
            # test_split=0.1,
            # tpu_cores = None,
        )
    model.save_model(model_dir=output_dir)


def predict(input):
    """ predicts a title from keywords
    input must be a list of strings, each item of the list must be a keyword
    """
    # chargement du modèle préentrainé
    model = trainer()
    model.load_model(model_dir="Models/titlegen/keytotext/")
    pred = model.predict(keywords=input, max_length=10, num_return_sequences=3, use_gpu=False, num_beams=3)
    return(pred)