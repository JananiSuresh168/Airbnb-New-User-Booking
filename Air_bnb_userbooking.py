# -*- coding: utf-8 -*-
"""Copy of airbnb-new-latest.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1iT8_mpLLt8CaqB3tavcgb5PUAMxuYW4G
"""

import os
from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
from datetime import datetime
import numpy as np

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import StratifiedKFold

from xgboost import XGBClassifier

import warnings
warnings.filterwarnings("ignore")

session=pd.read_csv("/content/drive/MyDrive/airbnb/sessions.csv")
print(session.shape)
session.head()

train_user=pd.read_csv("/content/drive/MyDrive/airbnb/train_users_2.csv")
print(train_user.shape)
train_user.head()

test_user=pd.read_csv("//content/drive/MyDrive/airbnb/test_users.csv")
print(test_user.shape)
test_user.head()

session.drop(['action_detail','device_type'],inplace=True,axis=1)
session.dropna(subset=['user_id','action'],inplace=True)
session.action_type=session.action_type.fillna('Other')
session.secs_elapsed=session.secs_elapsed.fillna(0)

session.head(5)

df_sess = session.groupby(['user_id']).agg({'action':'count','secs_elapsed':'sum'}).reset_index()
df_sess.head()

df_sess.columns

train_user_df=train_user.merge(df_sess, left_on=['id'],
                               right_on=['user_id'],how='left').drop(['user_id'],axis=1).reset_index(drop=True)
train_user_df.shape

test_user_df=test_user.merge(df_sess,left_on=['id'],
                               right_on=['user_id'],how='left').drop(['user_id'],axis=1).reset_index(drop=True)
test_user_df.shape

train_user_df.head(10)

# filling null columns of secs_elapsed, action and action_type columns with -1
train_user_df.secs_elapsed.fillna(-1,inplace=True)
train_user_df.action.fillna(-1,inplace=True)

train_user_df['secs_elapsed']=train_user_df['secs_elapsed'].astype('int64')
train_user_df['action']=train_user_df['action'].astype('int64')

test_user_df.secs_elapsed.fillna(-1,inplace=True)
test_user_df.action.fillna(-1,inplace=True)

test_user_df['secs_elapsed']=test_user_df['secs_elapsed'].astype('int64')
test_user_df['action']=test_user_df['action'].astype('int64')

train_user_df.isnull().sum()/train_user_df.shape[0] *100



"""## Data Cleaning"""

# Cleaning

df =  train_user_df.dropna(axis = 0, how = 'any')
df.shape

train_user_df.shape

# imbalanced dataset
import matplotlib.pyplot as plt
import seaborn as sn


order1 = train_user_df['country_destination'].value_counts()
order2 = order1.index
plt.figure(figsize=(7,5))
sn.countplot(train_user_df['country_destination'],order=order2)
plt.xlabel('Country Destination')
plt.ylabel('Country Destination Count')
for i in range(order1.shape[0]):
    count = order1[i]
    strg = '{:0.2f}%'.format(100*count/train_user_df.shape[0])
    plt.text(i,count+1000,strg,ha='center')

plt.figure(figsize=(14,5))
sn.set(style = 'darkgrid')
sn.set_context("talk")
pal = sn.color_palette("ch:s=.25,rot=-.25", len(gender))
sn.set(style="whitegrid", color_codes=True)
gender = train_user['gender'].value_counts()
rank = gender.argsort().argsort() 
sn.countplot('gender', data = train_user,order = train_user['gender'].value_counts().index, palette=np.array(pal[::-1])[rank])

for i in range(gender.shape[0]):
    range_count = gender[i]
    per = round(((range_count*100)/train_user.shape[0]),2)
    percent = '{}%'.format(per)
    plt.text(i,range_count,percent)
plt.xlabel('Gender')
plt.ylabel('Count')
plt.xticks(rotation = 45)
plt.title('Percentage Distribution of Gender field')
plt.show()

#Plotting the boxplot of 'age' to confirm the presence of outliers :

plt.figure(figsize=(10,5))
sn.set(style='darkgrid')
sn.set_context('talk')
sn.boxplot(train_user_df['age'].dropna())
plt.show()

# Handling null values and separating date, month and year 

# clubbing gender values having unknown and other 
train_user_df.gender.replace('-unknown-', 'OTHER', inplace=True)

# filling null age values with median = 34
train_user_df['age'].fillna(34,inplace=True)

train_user_df['timestamp_first_active']=train_user_df['timestamp_first_active'].apply(lambda s:datetime(year=int(str(s)[0:4]), month=int(str(s)[4:6]), 
                                                                                day=int(str(s)[6:8])).strftime('%Y-%m-%d'))

train_user_df['timestamp_first_active']=train_user_df['timestamp_first_active'].astype('datetime64[ns]')
train_user_df['age']=train_user_df['age'].astype('int64')
train_user_df['date_account_created']=train_user_df['date_account_created'].astype('datetime64[ns]')

train_user_df['dac_year']=train_user_df['date_account_created'].dt.year
train_user_df['dac_month']=train_user_df['date_account_created'].dt.month
train_user_df['dac_day']=train_user_df['date_account_created'].dt.day

train_user_df['tfa_year']=train_user_df['timestamp_first_active'].dt.year
train_user_df['tfa_month']=train_user_df['timestamp_first_active'].dt.month
train_user_df['tfa_day']=train_user_df['timestamp_first_active'].dt.day


# clubbing categories
train_user_df.signup_app.replace(['iOS','Android'],'SmartDevice',inplace=True)
        
train_user_df.drop(['date_first_booking','date_account_created','timestamp_first_active','first_device_type','first_browser'],axis=1,inplace=True)

#NULL test data
test_user_df.gender.replace('-unknown-', 'OTHER', inplace=True)
test_user_df['age'].fillna(-1,inplace=True)

test_user_df['timestamp_first_active']=test_user_df['timestamp_first_active'].apply(lambda s:datetime(year=int(str(s)[0:4]), month=int(str(s)[4:6]), 
                                                                                day=int(str(s)[6:8])).strftime('%Y-%m-%d'))

test_user_df['timestamp_first_active']=test_user_df['timestamp_first_active'].astype('datetime64[ns]')
test_user_df['age']=test_user_df['age'].astype('int64')
test_user_df['date_account_created']=test_user_df['date_account_created'].astype('datetime64[ns]')

test_user_df['dac_year']=test_user_df['date_account_created'].dt.year
test_user_df['dac_month']=test_user_df['date_account_created'].dt.month
test_user_df['dac_day']=test_user_df['date_account_created'].dt.day

test_user_df['tfa_year']=test_user_df['timestamp_first_active'].dt.year
test_user_df['tfa_month']=test_user_df['timestamp_first_active'].dt.month
test_user_df['tfa_day']=test_user_df['timestamp_first_active'].dt.day


test_user_df.signup_app.replace(['iOS','Android'],'SmartDevice',inplace=True)
      
test_user_df.drop(['date_first_booking','date_account_created','timestamp_first_active','first_device_type','first_browser'],axis=1,inplace=True)

train_user_df.head()

train_user_df.info()

"""# Age imputation"""

import matplotlib.pyplot as plt

plt.figure(figsize=(10,5))
sn.set(style='darkgrid')
sn.set_context('talk')
sn.boxplot(train_user_df['age'].dropna())
plt.show()

train_user_df.drop(train_user_df[train_user_df['age'] < 15].index, inplace = True)
train_user_df.drop(train_user_df[train_user_df['age'] > 110].index, inplace = True)

test_user_df.drop(test_user_df[test_user_df['age'] < 15].index, inplace = True)
test_user_df.drop(test_user_df[test_user_df['age'] > 110].index, inplace = True)

# Removed outlier graph

plt.figure(figsize=(10,5))
sn.set(style='darkgrid')
sn.set_context('talk')
sn.boxplot(train_user_df['age'].dropna())
plt.show()

train_user_df.info()

"""# *Skewness in age*"""

train_user_df['age'].skew(skipna = True)

import matplotlib.pyplot as plt


plt.hist(train_user_df['age'])

import math

d  = train_user_df['age'].map(lambda x: math.log(x))
df_age = pd.DataFrame(data=d,columns=['age'])

train_user_df['age'] = df_age['age']

# repeating same for test data

d  = test_user_df['age'].map(lambda x: math.log(x))
df_age = pd.DataFrame(data=d,columns=['age'])

test_user_df['age'] = df_age['age']

df_age.skew(skipna = True)

import matplotlib.pyplot as plt


plt.hist(df_age['age'])

"""# correlation matrix:"""



temp = train_user_df.corr()
temp

import seaborn as sn
import matplotlib.pyplot as plt

plt.figure(figsize=(17, 14))
svm = sn.heatmap(train_user_df.corr(), annot=True)

figure = svm.get_figure()    
figure.savefig('svm_conf.png', dpi=1000)

# removing timestamp first active

train_user_df.drop(['tfa_year','tfa_month','tfa_day'], axis = 1, inplace = True)

# removing timestamp first active

test_user_df.drop(['tfa_year','tfa_month','tfa_day'], axis = 1, inplace = True)

train_user_df.head()

train_user_df.columns.map(lambda x: print(x, "   ", len(train_user_df[x].value_counts())))

"""## Test train split"""

train_user_df.describe()

import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# encoding

temp_train = train_user_df.drop(['country_destination','id'], axis = 1)
temp_y = train_user_df['country_destination']

cato = temp_train.select_dtypes(include=['object']).copy()
onehot = pd.get_dummies(cato,columns = cato.columns)
# print(onehot.shape)

temp_train = temp_train.drop(cato.columns,axis=1)
temp_train = pd.concat([temp_train, onehot],axis=1)

from sklearn.model_selection import train_test_split

x = train_user_df.drop(['country_destination','id'],axis = 1)
y = train_user_df.country_destination

train_x, test_x, train_y, test_y = train_test_split( temp_train , temp_y, test_size=0.2, random_state=1)

tempx_train, tempx_test, tempy_train, tempy_test = train_test_split( train_x , train_y, test_size=0.1, random_state=0)

test_x = pd.concat([test_x, tempx_test], ignore_index=True)
test_y = pd.concat([test_y, tempy_test], ignore_index=True)

test_x.shape, train_x.shape, test_y.shape, train_y.shape



train_x[:5], train_y[:5]

scaler = StandardScaler()

# Fit on training set only.
scaler.fit(train_x)

# Apply transform to both the training set and the test set.
train_x = scaler.transform(train_x)
test_x = scaler.transform(test_x)

"""## LDA"""

# optimizing LDA

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
  

model = LinearDiscriminantAnalysis()
# define model evaluation method
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
# define grid
grid = dict()
grid['solver'] = ['svd', 'lsqr', 'eigen']
# define search
search = GridSearchCV(model, grid, scoring='f1_micro', cv=cv, n_jobs=-1)
# perform the search
results = search.fit(train_x, train_y)
# summarize
print('Mean Accuracy: %.3f' % results.best_score_)
print('Config: %s' % results.best_params_)

from numpy import arange
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

model = LinearDiscriminantAnalysis(solver='lsqr')
# define model evaluation method
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
# define grid
grid = dict()
grid['shrinkage'] = [0.1,0.4, 0.7]
# define search
search = GridSearchCV(model, grid, scoring='accuracy', cv=cv, n_jobs=-1)
# perform the search
results = search.fit(train_x, train_y)
# summarize
print('Mean Accuracy: %.3f' % results.best_score_)
print('Config: %s' % results.best_params_)

from numpy import arange
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

lda = LinearDiscriminantAnalysis(solver='svd')

X_lda = lda.fit_transform(train_x, train_y)

X_test_lda = lda.fit_transform(test_x, test_y)

lda_var_ratios = lda.explained_variance_ratio_

def select_n_components(var_ratio, goal_var: float) -> int:
    # Set initial variance explained so far
    total_variance = 0.0
    
    # Set initial number of features
    n_components = 0
    
    # For the explained variance of each feature:
    for explained_variance in var_ratio:
        
        # Add the explained variance to the total
        total_variance += explained_variance
        
        # Add one to the number of components
        n_components += 1
        
        # If we reach our goal level of explained variance
        if total_variance >= goal_var:
            # End the loop
            break
            
    # Return the number of components
    return n_components

select_n_components(lda_var_ratios, 0.99)

from sklearn.metrics import accuracy_score, f1_score


preds = lda.predict(test_x)
acc = accuracy_score(test_y, preds)
f1 = f1_score(test_y, preds, pos_label='positive',
                                           average='micro')

acc, f1

from sklearn.ensemble import RandomForestClassifier

rfc = RandomForestClassifier(n_estimators=100, n_jobs=-1)
rfc.fit(X_lda, train_y)

rfc.get_params()

ypred = rfc.predict(X_test_lda)

from sklearn.metrics import classification_report


print(classification_report(test_y, ypred))

"""## PCA"""

# PCA

pca = PCA(.95)
pca.fit(train_x)
X_train_pca = pca.transform(train_x)
X_test_pca = pca.transform(test_x)

# print(pd.DataFrame(pca.components_,columns= X_train.columns,index = ['PC-1','PC-2','PC-3','PC-4','PC-5','PC-6','PC-7','PC-8','PC-9','PC-10', 'PC-11', 'PC-12']))
comp_check = pca.explained_variance_ratio_
num_comps = comp_check.shape[0]
print("Using components, we can explain {}% of the variability in the original data.".format(comp_check.sum()))



# pca variance chart
exp_var_cumul = np.cumsum(pca.explained_variance_ratio_)
plt = px.area(
  x=range(1, exp_var_cumul.shape[0] + 1),
  y=exp_var_cumul,
  labels={"x": "# Components", "y": "Explained Variance"}
)

plt.show()

"""## Modelling"""

# Encoding target variable

le = LabelEncoder()
train_y = le.fit_transform(train_y)

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import RandomizedSearchCV

# Number of trees in random forest
n_estimators = [200, 400, 600]
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
random_grid = {'n_estimators': n_estimators,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               }
print(random_grid)

rf = RandomForestClassifier()
rf_random = RandomizedSearchCV(estimator = rf, scoring = 'f1_weighted', param_distributions = random_grid, cv = 2, n_iter = 100, verbose=2, random_state=42, n_jobs = -1)
# Fit the random search model
rf_random.fit(X_train_pca, train_y)

rf_random.best_params_

pred_y = rf_random.best_estimator_.predict(X_test_pca)

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

import matplotlib.pyplot as plt
import seaborn as sn

print(classification_report(test_y, le.inverse_transform(pred_y)))
cm = confusion_matrix(test_y, le.inverse_transform(pred_y))


plt.figure(figsize=(14,10))
sn = sn.heatmap(data=cm,linewidths=.5, annot=True,square = True,  cmap = 'Blues',fmt='g')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
plt.show()
figure = sn.get_figure()
# figure.savefig('cm_rf.png', dpi=1000)

print('\n\nAccuracy score for random forest: ', accuracy_score(test_y, le.inverse_transform(pred_y)))
print(f1_score(test_y, le.inverse_transform(pred_y),average = "weighted"))

from sklearn.metrics import f1_score,recall_score, precision_score

print("F1 score: ", f1_score(test_y, le.inverse_transform(pred_y), pos_label='positive',average='micro'))
print("Recall score: ", recall_score(test_y, le.inverse_transform(pred_y), pos_label='positive', average='micro'))

from numpy import mean
from numpy import std
from numpy import absolute
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold

# ridge algorithm without resampling

from sklearn.linear_model import RidgeClassifier, RidgeClassifierCV
from numpy import arange
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedKFold
from sklearn.linear_model import Ridge
from sklearn.datasets import make_blobs
from sklearn.model_selection import RepeatedStratifiedKFold

alpha = [0.1, 0.3, 0.6, 1]

grid = dict(alpha=alpha)

# rc = RidgeClassifierCV(alphas= alpha, class_weight= 'balanced', fit_intercept=True,
#                 normalize=False)
# print(rc)
model = RidgeClassifier()

cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
grid_search = GridSearchCV(estimator=model, param_grid=grid, n_jobs=-1, cv=cv, scoring='f1_weighted',error_score=0)
grid_result = grid_search.fit(X_train_pca, train_y)
# summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))

rc = RidgeClassifier(alpha = 1)
rc.fit(X_train_pca, train_y)

rc.get_params()

ypred = rc.predict(X_test_pca)

from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score,recall_score, precision_score


print(classification_report(test_y, le.inverse_transform(ypred)))
cm = confusion_matrix(test_y, le.inverse_transform(ypred))

  
plt.figure(figsize=(25,7))
sn.heatmap(data=cm,linewidths=.5, annot=True,square = True,  cmap = 'Blues',fmt='g')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
# all_sample_title = 'KNN Accuracy Score: {0}'.format(clf.score(X, y))
# plt.title(all_sample_title, size = 15)
plt.show()

print(accuracy_score(test_y, le.inverse_transform(ypred)))
print(f1_score(test_y, le.inverse_transform(ypred), average = "weighted"))

# Resampling using SMOTE and random under sampling

from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline


sampling_strategy_over = {0: 800, 1: 3000, 2: 2000, 3: 3000, 4: 5000, 5: 3000, 6: 3000, 8: 1000, 9: 300, 11: 15000}
sampling_strategy_under = {7: 50000}

under = RandomUnderSampler(sampling_strategy = sampling_strategy_under)
over = SMOTE(sampling_strategy_over)
steps = [('u', under),('o', over)]
pipeline = Pipeline(steps=steps)

X_sm, y_sm = pipeline.fit_resample(X_train_pca, train_y)

import collections

counter=collections.Counter(y_sm)
print(counter)

from sklearn.linear_model import RidgeClassifier


rc = RidgeClassifier(alpha=1, class_weight= 'balanced', copy_X=True, fit_intercept=True,
                max_iter=None, normalize=False, random_state= 1,
                solver='svd')
print(rc)

rc.fit(X_sm, y_sm)
ypred = rc.predict(X_test_pca)

len(X_sm), len(y_sm)

import matplotlib.pyplot as plt


print(classification_report(test_y, le.inverse_transform(ypred)))
cm = confusion_matrix(test_y, le.inverse_transform(ypred))

  
plt.figure(figsize=(15,8))
sn.heatmap(data=cm,linewidths=.5, annot=True,square = True,  cmap = 'Blues',fmt='g')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
plt.show()

print(accuracy_score(test_y, le.inverse_transform(ypred)))
print(f1_score(test_y, le.inverse_transform(ypred), average="weighted"))

#  random forest with resampling

rf = RandomForestClassifier()
rf.fit(X_sm, y_sm)

ypred = rf.predict(X_test_pca)

import matplotlib.pyplot as plt
import seaborn as sn
from sklearn.metrics import f1_score

print(classification_report(test_y, le.inverse_transform(ypred)))
cm = confusion_matrix(test_y, le.inverse_transform(ypred))

  
plt.figure(figsize=(15,8))
sn.heatmap(data=cm,linewidths=.5, annot=True,square = True,  cmap = 'Blues',fmt='g')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
plt.show()

print(accuracy_score(test_y, le.inverse_transform(ypred)))
print(f1_score(test_y, le.inverse_transform(ypred), average="weighted"))



# KNN

from sklearn.neighbors import KNeighborsClassifier

clf = KNeighborsClassifier(n_neighbors=30)
clf.fit(X_train_pca, train_y)

y_pred = clf.predict(X_test_pca)

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV

#List Hyperparameters that we want to tune.
leaf_size = [int(x) for x in np.linspace(start = 10, stop = 50, num = 5)]
n_neighbors = [int(x) for x in np.linspace(start = 10, stop = 50, num = 3)]
p=[1,2]
#Convert to dictionary
hyperparameters = dict(leaf_size=leaf_size, n_neighbors=n_neighbors, p=p)
#Create new KNN object
knn_2 = KNeighborsClassifier()
#Use GridSearch
clf = GridSearchCV(knn_2, hyperparameters, cv=10)
#Fit the model
knn_model = clf.fit(X_train_pca, train_y)
#Print The value of best Hyperparameters
print('Best leaf_size:', knn_model.best_estimator_.get_params()['leaf_size'])
print('Best p:', knn_model.best_estimator_.get_params()['p'])
print('Best n_neighbors:', knn_model.best_estimator_.get_params()['n_neighbors'])

import matplotlib.pyplot as plt


print(classification_report(test_y, le.inverse_transform(y_pred)))
cm = confusion_matrix(test_y, le.inverse_transform(y_pred))

  
plt.figure(figsize=(15,12))
sn.heatmap(data=cm,linewidths=.5, annot=True,square = True,  cmap = 'Blues',fmt='g')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
plt.show()

print(accuracy_score(test_y, le.inverse_transform(y_pred)))

# https://machinelearningmastery.com/extra-trees-ensemble-with-python/

from sklearn.ensemble import ExtraTreesClassifier
from numpy import mean
from numpy import std
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.ensemble import ExtraTreesClassifier


def get_models():
	models = dict()
	# define number of trees to consider
	n_trees = [10,50,100]
	for n in n_trees:
		models[str(n)] = ExtraTreesClassifier(n_estimators=n)
	return models
 
# evaluate a given model using cross-validation
def evaluate_model(model, X, y):
	# define the evaluation procedure
	cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
	# evaluate the model and collect the results
	scores = cross_val_score(model, X, y, scoring='f1_weighted', cv=cv, n_jobs=-1)
	return scores


# get the models to evaluate
models = get_models()
# evaluate the models and store results
results, names = list(), list()
for name, model in models.items():
	# evaluate the model
	scores = evaluate_model(model, X_train_pca, train_y)
	# store the results
	results.append(scores)
	names.append(name)
	# summarize the performance along the way
	print('>%s %.3f (%.3f)' % (name, mean(scores), std(scores)))
# plot model performance for comparison

import matplotlib.pyplot as plt


plt.boxplot(results, labels=names, showmeans=True)
plt.xlabel('Extra Trees Ensemble Size')
plt.ylabel('Classification Accuracy')
plt.title('Effect of tuning Extra Trees Ensemble Size on Accuracy')
plt.show()

# from numpy import arrange

# get a list of models to evaluate
def get_models():
	models = dict()
	# explore number of features from 1 to 10
	for i in [1, 2, 4, 6]:
		models[str(i)] = ExtraTreesClassifier(max_features=i)
	return models
 
# evaluate a given model using cross-validation
def evaluate_model(model, X, y):
	# define the evaluation procedure
	cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
	# evaluate the model and collect the results
	scores = cross_val_score(model, X, y, scoring='f1_weighted', cv=cv, n_jobs=-1)
	return scores
 
# get the models to evaluate
models = get_models()
# evaluate the models and store results
results, names = list(), list()
for name, model in models.items():
	# evaluate the model
	scores = evaluate_model(model, X_train_pca, train_y)
	# store the results
	results.append(scores)
	names.append(name)
	# summarize the performance along the way
	print('>%s %.3f (%.3f)' % (name, mean(scores), std(scores)))

plt.boxplot(results, labels=names, showmeans=True)
plt.xlabel('Extra Trees Feature Set Size')
plt.ylabel('Classification Accuracy')
plt.title('Effect of tuning Extra Trees Feature Set Size on Accuracy')
plt.show()

import seaborn as sn
from sklearn.ensemble import ExtraTreesClassifier

clf = ExtraTreesClassifier(n_estimators=50, max_features=1)
clf.fit(X_train_pca, train_y)

y_pred = clf.predict(X_test_pca)

print(classification_report(test_y, le.inverse_transform(y_pred)))
cm = confusion_matrix(test_y, le.inverse_transform(y_pred))
plt.figure(figsize=(15,8))
sn.heatmap(data=cm,linewidths=.5, annot=True,square = True,  cmap = 'Blues',fmt='g')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
plt.show()

print(accuracy_score(test_y, le.inverse_transform(y_pred)))
print(f1_score(test_y, le.inverse_transform(y_pred), average = "weighted"))

# Decision Tree

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from numpy import arange
from numpy import mean
from numpy import std


# get a list of models to evaluate
def get_models():
	models = dict()
	for i in [12,15,50,80,100]:
		models[str(i)] = DecisionTreeClassifier(max_depth=i)
	return models

# evaluate a give model using cross-validation
def evaluate_model(model):
	cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
	scores = cross_val_score(model, X_train_pca,train_y, scoring='f1_weighted', cv=cv, n_jobs=-1)
	return scores

# get the models to evaluate
models = get_models()
# evaluate the models and store results
results, names = list(), list()
for name, model in models.items():
	scores = evaluate_model(model)
	results.append(scores)
	names.append(name)
	print('>%s %.3f (%.3f)' % (name, mean(scores), std(scores)))


# Predicting the values of test data
# y_pred = dtree.predict(X_test_pca)

plt.boxplot(results, labels=names, showmeans=True)
plt.xlabel('Max depth of decision tree')
plt.ylabel('Classification Accuracy')
plt.show()

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV

criterion = ['gini', 'entropy']
max_depth = [12]
parameters = dict(    criterion=criterion,
                      max_depth=max_depth)

tree = DecisionTreeClassifier()

model_GS = GridSearchCV(tree, parameters, scoring="f1_weighted")
model_GS.fit(X_train_pca, train_y)


# Predicting the values of test data
# y_pred = dtree.predict(X_test_pca)

model_GS.best_params_

y_pred = model_GS.predict(X_test_pca)

import matplotlib.pyplot as plt
import seaborn as sn

print(classification_report(test_y, le.inverse_transform(y_pred)))
cm = confusion_matrix(test_y, le.inverse_transform(y_pred))
plt.figure(figsize=(10,10))
sn.heatmap(data=cm,linewidths=.5, annot=True,square = True,  cmap = 'Blues',fmt='g')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
plt.show()

print(accuracy_score(test_y, le.inverse_transform(y_pred)))
print(f1_score(test_y, le.inverse_transform(y_pred), average = "weighted"))

# xg - boost
from xgboost import XGBClassifier

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from xgboost import XGBClassifier
from numpy import arange
from numpy import mean
from numpy import std

#  get a list of models to evaluate
def get_models():
	models = dict()
	trees = [10, 50, 100]
	for n in trees:
		models[str(n)] = XGBClassifier(n_estimators=n)
	return models
 
# evaluate a give model using cross-validation
def evaluate_model(model):
  cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
  print(cv)
  scores = cross_val_score(model, X_train_pca,train_y, scoring='f1_weighted', cv=cv, n_jobs=-1)
  return scores

# get the models to evaluate
models = get_models()
# evaluate the models and store results
results, names = list(), list()
for name, model in models.items():
	scores = evaluate_model(model)
	results.append(scores)
	names.append(name)
	print('>%s %.3f (%.3f)' % (name, mean(scores), std(scores)))
# plot model performance for comparison
plt.boxplot(results, labels=names, showmeans=True)
plt.show()

import matplotlib.pyplot as plt

plt.boxplot(results, labels=names, showmeans=True)
plt.xlabel('N_estimators')
plt.ylabel('Classification Accuracy')
plt.show()

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
from numpy import arange
from numpy import mean
from numpy import std


model = XGBClassifier()
learning_rate = [0.01, 0.1, 0.3, 0.5]

grid = dict(learning_rate=learning_rate, n_estimators=[10])
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
grid_search = GridSearchCV(estimator=model, param_grid=grid, n_jobs=-1, cv=cv, scoring='f1_weighted',error_score=0)
grid_result = grid_search.fit(X_train_pca,train_y )
# summarize results
print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
means = grid_result.cv_results_['mean_test_score']
stds = grid_result.cv_results_['std_test_score']
params = grid_result.cv_results_['params']
for mean, stdev, param in zip(means, stds, params):
    print("%f (%f) with: %r" % (mean, stdev, param))

model.get_params()

# Predicting the values of test data
y_pred = model.predict(X_test_pca)

import matplotlib.pyplot as plt
import seaborn as sn

print(classification_report(test_y, le.inverse_transform(y_pred)))
cm = confusion_matrix(test_y, le.inverse_transform(y_pred))
plt.figure(figsize=(12,8))
sn.heatmap(data=cm,linewidths=.5, annot=True,square = True,  cmap = 'Blues',fmt='g')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
plt.show()

print(accuracy_score(test_y, le.inverse_transform(y_pred)))