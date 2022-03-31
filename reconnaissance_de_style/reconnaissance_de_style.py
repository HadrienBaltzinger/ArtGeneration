# !pip install fastai --upgrade

from unittest import result
from fastai.vision.all import *
from fastai.metrics import error_rate, accuracy
import numpy as np
import os
from PIL import Image

def import_resize_data(database_path):
    data = ImageDataLoaders.from_folder(database_path, valid_pct=0.2, item_tfms=Resize(100))
    return data

def create_CNN(data):
    learner = cnn_learner(data, models.resnet50, metrics=[accuracy, error_rate])
    return learner

def find_good_learning_rate(learner):
    learning_rate = learner.lr_find()
    return learning_rate

def fit_model(learner,learning_rate = 1e-2):
    learner.fit_one_cycle(10, learning_rate)
    return learner

def save_model(learner, save_path):
    learner.save(save_path+"style-r50")
    learner.export(save_path+"learner-model")
    print("model saved at " + save_path)

def load_model(load_path):
    learner = load_learner(load_path+"learner-model")
    model = learner.load(load_path+"style-r50")
    return model

def get_topk_prediction(learner,img_path,k):
    result = []
    img = Image.open(img_path).convert('RGB').resize((100,100), Image.ANTIALIAS)
    img = np.array(img)
    pred = learner.predict(img)
    topk = torch.topk(pred[2], k)
    for i in range(3):
        print(f'{learner.dls.vocab[topk.indices[i]]}: {100*topk.values[i]:.2f}%')
        result.append([learner.dls.vocab[topk.indices[i]],float(100*topk.values[i])])
    return result

def update_model(database_path,save_path):
    data = import_resize_data(database_path)
    learner = create_CNN(data)
    learning_rate = find_good_learning_rate(learner)
    learner = fit_model(learner,learning_rate)
    save_model(learner, save_path)

def predict_result(img_path,load_path,k = 3):
    model = load_model(load_path)
    result = get_topk_prediction(model,img_path,k)
    return result

# update_model('/content/drive/Shareddrives/PFE artists/data/wikiart-base','/content/drive/Shareddrives/PFE artists/reconnaissance_de_style/')
predicted = predict_result('/content/drive/Shareddrives/PFE artists/reconnaissance_de_style/test/test_baroque.jpg','/content/drive/Shareddrives/PFE artists/reconnaissance_de_style/')
print(predicted)