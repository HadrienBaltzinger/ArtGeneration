# !pip install fastai --upgrade

from unittest import result
from fastai.vision.all import *
from fastai.metrics import error_rate, accuracy
import numpy as np
import os
from PIL import Image

# test_img_path = '/content/drive/Shareddrives/PFE artists/reconnaissance_de_style/test/test_baroque.jpg'
model_path = 'reconnaissance_de_style/'

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
    # model = learner.load(load_path+"style-r50")
    return learner #model

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

def update_model(database_path,save_path = model_path):
    """
    function to retrain model from a database and save it in 'save_path'

    input: 
        database_path : string : path to the database
        save_path     : string : path to save the new model

    output:
        None
    """
    data = import_resize_data(database_path)
    learner = create_CNN(data)
    # uncomment this too lines if you want to find a better learning rate
    # learning_rate = find_good_learning_rate(learner)
    # learner = fit_model(learner,learning_rate)
    # uncomment this line if you want an approximate good learning rate
    learner = fit_model(learner)
    save_model(learner, save_path)

def predict_result(img_path,load_path = model_path,k = 3):
    """
    function to get the probability of an image 'img_path' to be in a class
    classe's names are stored in model.dls.vocab

    input:
        img_path  : string : path to the image you need prediction
        load_path : string : path to the saved model you want to use
        k         : int    : top k more likely in all classes

    output : 
        result    : array(k,2) :  return an array of shape k*2, each line contains [class_name(string),probability(float)]
    
    """
    model = load_model(load_path)
    result = get_topk_prediction(model,img_path,k)
    return result

# uncomment this line if you want to retrain model ( > 2h )
# update_model(img_database_path,model_path)

# uncomment this line if you want to get result from an image
# predicted = predict_result(test_img_path,model_path)
# print(predicted)