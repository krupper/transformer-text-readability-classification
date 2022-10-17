# Import dependencies
from sklearn import svm, datasets
import sklearn.model_selection as model_selection
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import pandas as pd
import numpy as np
from sklearn.utils import shuffle
from sklearn.utils import resample
from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
import multiprocessing

if __name__ == '__main__':
    # multi feature corpus cannot be published due to copyright reasons
    df = pd.read_csv('/SVM Approach/multi-feature_new.csv')
    print("Size:", len(df))

    # Resample to handle the imbalanced dataset
    minority_samples = df["label"].value_counts().tolist()[-1] # number of sample in the lowest category
    df_minority = df[df.label == 0]

    for i in range(1, 4):
      df_majority = df[df.label == i]

      if i is 2:
        limit_samples = int(minority_samples * 1.4)
      elif i is 1:
        limit_samples = int(minority_samples * 1.1)
      else:
        limit_samples = minority_samples

      # Downsample majority class
      df_majority_downsampled = resample(df_majority, 
                                      replace=False,    # sample without replacement
                                      n_samples=limit_samples,     # to match minority class
                                      random_state=123) # reproducible results

      # Combine minority class with downsampled majority class
      df_minority = pd.concat([df_majority_downsampled, df_minority])

    df = df_minority

    # Print number of rows for categories
    print(df["label"].value_counts())

    # Select specific columns as features
    columns = [
        "number_of_words",
        "number_of_sentences",
        "abbreviations",
        "abstract_words",
        "anglicism",
        "complicated_words",
        "flesch_score",
        "genitive",
        "gsmog_score",
        "lix_score",
        "long_words",
        "negations",
        "numberals",
        "numbers",
        "passive_voice",
        "relative_clause",
        "roman_numbers",
        "special_characters",
        "specialist_terms",
        "subclauses",
        "subjunctive",
        "two_information_units",
        "wstf_4_score"
        ]

    X = df[columns].to_numpy()


    # Split dataset into train and test sets
    y = df["label"].to_numpy()
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, train_size=0.80, test_size=0.20, random_state=101)

    # Scale data
    scaler = preprocessing.StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)

    scaler = preprocessing.StandardScaler().fit(X_test)
    X_test = scaler.transform(X_test)

    # Add "label" column again for later usage
    columns.append("label")
    df = df[columns]


    ####### Hyperparameter optimization #######

    # defining parameter range
    param_grid = {'C': [0.001, 0.1, 0.5, 1],
                  'gamma': [1, 0.1, 0.01, 0.001],
                  'kernel': ["rbf", "poly", "linear", "sigmoid"]}

    n_cpus = multiprocessing.cpu_count()
    print(n_cpus)

    grid = GridSearchCV(SVC(), param_grid, refit=True, verbose=3, n_jobs=-1)

    # fitting the model for grid search
    grid.fit(X_train, y_train)

    # print best parameter after tuning
    print(grid.best_params_)

    # print how the model looks after hyper-parameter tuning
    print(grid.best_estimator_)

    grid_predictions = grid.predict(X_test)

    # print classification report
    print(classification_report(y_test, grid_predictions))