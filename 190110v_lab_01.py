# -*- coding: utf-8 -*-
"""190110V - Lab 01.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sCkqhGGDP-2PUOQz2kK5cTljaNRKxG8Q
"""

# import libraries
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, mean_squared_error
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# read the test and train data files
train_df = pd.read_csv("train.csv")
test_df = pd.read_csv("valid.csv")
test_df_ = pd.read_csv("test.csv")

def to_csv(predictions_old, predictions_new, reduced_X_train, label_no):
    data = []
    cols = ["Predicted labels before feature engineering", "Predicted labels after feature engineering", "No of new features"]

    for index in range(1, 257):
        cols.append(f"new_feature_{index}")

    for index, pred in enumerate(predictions_old):
        data.append([predictions_old[index], predictions_new[index]])

    final_no_of_features = reduced_X_train.shape[1]
    for index, row in enumerate(data):
        data[index].append(final_no_of_features)
        if index < len(reduced_X_train):
            data[index] = np.concatenate((data[index], reduced_X_train[index]))

    blank_array = np.empty((1, (256 - final_no_of_features)))
    blank_array.fill(np.nan)
    for index,row in enumerate(data):
        data[index] = np.concatenate((data[index], blank_array[0]))

    data_frame = pd.DataFrame(data, columns=cols)
    data_frame.to_csv(f"190110V_{label_no}.csv",na_rep='')

def scale_features(X_train, X_test, X_test_):
    scaler = StandardScaler()
    scaler.fit(X_train)

    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)
    X_test_ = scaler.transform(X_test_)
    return X_train, X_test, X_test_

def fit_into_RFC(X_train, X_test,X_test_, Y_train, Y_test):
    model = RandomForestClassifier()
    model.fit(X_train, Y_train)
    y_pred = model.predict(X_test)
    y_pred_ = model.predict(X_test_)
    print(classification_report(Y_test, y_pred))

    return model, y_pred, y_pred_

def fit_transform_PCA(X_train, X_test, X_test_, threshold):
    pca=PCA(threshold)
    pca = pca.fit(X_train)

    x_train_pca=pca.fit_transform(X_train)
    x_test_pca = pca.transform(X_test)
    x_test_pca_ = pca.transform(X_test_)

    return x_train_pca, x_test_pca, x_test_pca_

def reduce_with_feature_importances(model,X_train, X_test, X_test_, threshold):
    importance = model.feature_importances_

    columns_to_delete = []
    for i,v in enumerate(importance):
        if v < threshold:
            columns_to_delete.append(i)
    X_train_reduced = np.delete(X_train,columns_to_delete,axis=1)
    X_test_reduced = np.delete(X_test,columns_to_delete,axis=1)
    X_test_reduced_ = np.delete(X_test_,columns_to_delete,axis=1)

    return X_train_reduced, X_test_reduced, X_test_reduced_

def fit_into_xgboost(X_train,X_test, X_test_, Y_train, Y_test):
    import xgboost as xgb

    regressor = xgb.XGBRegressor()
    regressor.fit(X_train,Y_train)
    Y_pred = regressor.predict(X_test)
    Y_pred_ = regressor.predict(X_test_)
    print(f"mean squared error: {mean_squared_error(Y_test,Y_pred)}")

    return Y_pred, Y_pred_

"""label 01"""

train_df_1 = train_df.iloc[:,:-3]
test_df_1 = test_df.iloc[:, :-3]
test_df_1_ = test_df_.iloc[:, :-4]

train_df_1.dropna(inplace=True)
test_df_1.dropna(inplace=True)
test_df_1_.dropna(inplace=True)

# splitting the test and train datasets into X and Y values
X_train_1= train_df_1.iloc[:,0:-1].values
Y_train_1 = train_df_1.iloc[:,-1].values
X_test_1 = test_df_1.iloc[:,0:-1].values
Y_test_1 = test_df_1.iloc[:,-1].values
X_test_1_ = test_df_1_.iloc[:, :].values

# scalling and fitting data
X_train_1, X_test_1, X_test_1_ = scale_features(X_train_1, X_test_1, X_test_1_)

# random forest classifier
model, y_pred_1, y_pred_1_ = fit_into_RFC(X_train_1, X_test_1, X_test_1_, Y_train_1,Y_test_1)

x_train_pca_1, x_test_pca_1, x_test_pca_1_ =fit_transform_PCA(X_train_1, X_test_1, X_test_1_, 0.97)

# random forest classifier
model, y_pred_1_after, y_pred_1_after_ = fit_into_RFC(x_train_pca_1, x_test_pca_1, x_test_pca_1_, Y_train_1,Y_test_1)

# dropping the features which have low score in feature importance
x_train_pca_reduced, x_test_pca_reduced, x_test_pca_reduced_ = reduce_with_feature_importances(model, x_train_pca_1, x_test_pca_1, x_test_pca_1_, 0.009)

x_train_pca_reduced.shape

# random forest classifier
model, y_pred_after, y_pred_after_ = fit_into_RFC(x_train_pca_reduced, x_test_pca_reduced, x_test_pca_reduced_, Y_train_1,Y_test_1)

to_csv(y_pred_1_, y_pred_after_, x_train_pca_reduced, "label_1")

"""label 02"""

train_df_2 = train_df.iloc[:, :-2]
test_df_2 = test_df.iloc[:, :-2]
test_df_2_ = test_df_.iloc[:, :-4]

train_df_2.drop(columns=["label_1"], inplace=True)
test_df_2.drop(columns=["label_1"], inplace=True)

train_df_2.dropna(inplace=True)
test_df_2.dropna(inplace=True)
test_df_2_.dropna(inplace=True)

# splitting the test and train datasets into X and Y values
X_train_2= train_df_2.iloc[:,0:-1].values
Y_train_2 = train_df_2.iloc[:,-1].values
X_test_2 = test_df_2.iloc[:,0:-1].values
Y_test_2 = test_df_2.iloc[:,-1].values
X_test_2_ = test_df_2_.iloc[:,: ].values

# scalling and fitting data
X_train_2, X_test_2, X_test_2_ = scale_features(X_train_2, X_test_2, X_test_2_)

#install xgboost
!pip install xgboost

Y_pred_2, Y_pred_2_ = fit_into_xgboost(X_train_2, X_test_2, X_test_2_, Y_train_2, Y_test_2)

X_train_pca_2, X_test_pca_2, X_test_pca_2_ =fit_transform_PCA(X_train_2, X_test_2, X_test_2_, 0.8)

X_train_pca_2.shape

Y_pred_2_after, Y_pred_2_after_ = fit_into_xgboost(X_train_pca_2, X_test_pca_2, X_test_pca_2_,Y_train_2, Y_test_2)

to_csv(Y_pred_2_ , Y_pred_2_after_, X_train_pca_2, "label_2")

"""label 03"""

train_df_3 = train_df.iloc[:, :-1]
test_df_3 = test_df.iloc[:, :-1]
test_df_3_ = test_df_.iloc[:, :-4]

train_df_3.drop(columns=["label_1", "label_2"], inplace=True)
test_df_3.drop(columns=["label_1", "label_2"], inplace=True)

test_df_3_.dropna(inplace=True)

X_train_3= train_df_3.iloc[:,0:-1].values
Y_train_3 = train_df_3.iloc[:,-1].values
X_test_3 = test_df_3.iloc[:,0:-1].values
Y_test_3 = test_df_3.iloc[:,-1].values
X_test_3_ = test_df_3_.iloc[:,:].values

# scalling and fitting data
X_train_3, X_test_3, X_test_3_ = scale_features(X_train_3, X_test_3, X_test_3_)

# random forest classifier
model, y_pred_3, y_pred_3_= fit_into_RFC(X_train_3, X_test_3, X_test_3_, Y_train_3,Y_test_3)

train_df_3['label_3'].value_counts().plot(kind='bar',title='Count of Label_3')

# resampling the data
from imblearn.combine import SMOTETomek

resampler = SMOTETomek(random_state=0)
X_train_3, Y_train_3 = resampler.fit_resample(X_train_3, Y_train_3)

X_train_pca_3, X_test_pca_3, X_test_pca_3_ =fit_transform_PCA(X_train_3, X_test_3, X_test_3_, 0.98)

model, Y_pred_3_after, Y_pred_3_after_  = fit_into_RFC(X_train_pca_3, X_test_pca_3, X_test_pca_3_, Y_train_3,Y_test_3)

# dropping the features which have low score in feature importance
x_train_pca_reduced, x_test_pca_reduced, x_test_pca_reduced_ = reduce_with_feature_importances(model, X_train_pca_3, X_test_pca_3, X_test_pca_3_, 0.008)

x_train_pca_reduced.shape

model, Y_pred_3_after, Y_pred_3_after_= fit_into_RFC(x_train_pca_reduced, x_test_pca_reduced, x_test_pca_reduced_, Y_train_3,Y_test_3)

to_csv(y_pred_3_, Y_pred_3_after_, x_train_pca_reduced, "label_3")

"""label 04"""

train_df_4 = train_df.iloc[:, :]
test_df_4 = test_df.iloc[:, :]
test_df_4_ = test_df_.iloc[:, :-4]

train_df_4.drop(columns=["label_1", "label_2", "label_3"], inplace=True)
test_df_4.drop(columns=["label_1", "label_2", "label_3"], inplace=True)

test_df_4_.dropna(inplace=True)

X_train_4= train_df_4.iloc[:,0:-1].values
Y_train_4 = train_df_4.iloc[:,-1].values
X_test_4 = test_df_4.iloc[:,0:-1].values
Y_test_4 = test_df_4.iloc[:,-1].values
X_test_4_ = test_df_4_.iloc[:, :].values

# random forest classifier
model, y_pred_4, y_pred_4_  = fit_into_RFC(X_train_4, X_test_4, X_test_4_, Y_train_4, Y_test_4)

X_train_pca_4, X_test_pca_4, X_test_pca_4_ = fit_transform_PCA(X_train_4, X_test_4, X_test_4_ , 0.97)

# random forest classifier
model, y_pred_4, y_pred_4_  = fit_into_RFC(X_train_pca_4, X_test_pca_4, X_test_pca_4_, Y_train_4, Y_test_4)

train_df_4['label_4'].value_counts().plot(kind='bar',title='Imbalanced Label_4')

X_train_pca_4, Y_train_4 = resampler.fit_resample(X_train_pca_4, Y_train_4)

# dropping the features which have low score in feature importance
x_train_pca_reduced, x_test_pca_reduced,x_test_pca_reduced_ = reduce_with_feature_importances(model, X_train_pca_4, X_test_pca_4, X_test_pca_4_, 0.015)

x_train_pca_reduced.shape

model, Y_pred_4_after, Y_pred_4_after_  = fit_into_RFC(x_train_pca_reduced, x_test_pca_reduced, x_test_pca_reduced_, Y_train_4, Y_test_4)

to_csv(y_pred_4_, Y_pred_4_after_ , x_train_pca_reduced, "label_4")

