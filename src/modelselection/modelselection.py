import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn import svm
import pickle

from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report

from sklearn.utils import shuffle

print('PROGRAM STARTED')

# self-drive
df_sd = pd.read_csv('../data/Twitter-sentiment-self-drive-DFE.csv', encoding='latin1')

# remove not relevant tweets
df_sd = df_sd[~df_sd['sentiment'].isin(['not_relevant'])]

# create the main dataframe by extracting the relevant rows
df = pd.concat([df_sd['text'], df_sd['sentiment']], axis=1, keys=['text', 'sentiment'])

# normalize the sentiment values ({1; 2; 3; 4; 5} => {-1; 0; 1})
df['sentiment'] = df['sentiment'].map({'1':-1, '2':-1, '3':0, '4':1, '5':1})
df_sd = df

print('self-drive loaded')

# text-emotion
df_te = pd.read_csv('../data/text_emotion.csv')
df_te = pd.concat([df_te['content'], df_te['sentiment']], axis=1, keys=['text', 'sentiment'])

# remove not relevant tweets
df_te = df_te[~df_te['sentiment'].isin(['empty'])]

# map words into integer values ({...} => {-1; 0; 1})
df_te['sentiment'] = df_te['sentiment'].map({
    'sadness':-1,
    'enthusiasm':1,
    'neutral':0,
    'worry':-1,
    'surprise':1,
    'love':1,
    'fun':1,
    'hate':-1,
    'happiness':1,
    'boredom':-1,
    'relief':1,
    'anger':-1})

# append the rows to the main dataframe
df = df.append(df_te)
# del df_te
print('text-emotion loaded')

# apple
df_ap = pd.read_csv('../data/Apple-Twitter-Sentiment-DFE.csv', encoding='latin1')
df_ap = pd.concat([df_ap['text'], df_ap['sentiment']], axis=1, keys=['text', 'sentiment'])

# remove not relevant tweets
df_ap = df_ap[~df_ap['sentiment'].isin(['not_relevant'])]

# normalize the sentiment values ({1; 3; 5} => {-1; 0; 1})
df_ap['sentiment'] = df_ap['sentiment'].map({'1':-1, '3':0, '5':1})

# append the rows to the main dataframe
df = df.append(df_ap)
# del df_ap
print('apple loaded')

# airline
df_ai = pd.read_csv('../data/Airline-Sentiment-2-w-AA.csv', encoding='latin1')
df_ai = pd.concat([df_ai['text'], df_ai['airline_sentiment']], axis=1, keys=['text', 'sentiment'])

# normalize the sentiment values ({'negative'; 'neutral'; 'positive'} => {-1; 0; 1})
df_ai['sentiment'] = df_ai['sentiment'].map({'negative':-1, 'neutral':0, 'positive':1})

# append the rows to the main dataframe
df = df.append(df_ai)
# del df_ai
print('airline loaded')

df['sentiment'] = df['sentiment'].map({-1:1, 0:3, 1:5})

SAMPLE_SIZE = 18144 # Number of neutral occurences
df = df.loc[df['sentiment'] == 5].sample(SAMPLE_SIZE).append(df.loc[df['sentiment'] == 3].sample(SAMPLE_SIZE)).append(df.loc[df['sentiment'] == 1].sample(SAMPLE_SIZE))
df = shuffle(df)
print('dataframe shuffled, filtered. READY')

# Array of vectorizers for the feature extraction step
vecs = [
    CountVectorizer(stop_words='english', ngram_range=(1, 1), lowercase=True),
    CountVectorizer(stop_words='english', ngram_range=(1, 1), lowercase=False),
    CountVectorizer(stop_words='english', ngram_range=(2, 2), lowercase=True),
    CountVectorizer(stop_words='english', ngram_range=(2, 2), lowercase=False),
    CountVectorizer(stop_words=None, ngram_range=(1, 1), lowercase=True),
    CountVectorizer(stop_words=None, ngram_range=(1, 1), lowercase=False),
    CountVectorizer(stop_words=None, ngram_range=(2, 2), lowercase=True),
    CountVectorizer(stop_words=None, ngram_range=(2, 2), lowercase=False),
    TfidfVectorizer(stop_words='english', ngram_range=(1, 1), lowercase=True),
    TfidfVectorizer(stop_words='english', ngram_range=(1, 1), lowercase=False),
    TfidfVectorizer(stop_words='english', ngram_range=(2, 2), lowercase=True),
    TfidfVectorizer(stop_words='english', ngram_range=(2, 2), lowercase=False),
    TfidfVectorizer(stop_words=None, ngram_range=(1, 1), lowercase=True),
    TfidfVectorizer(stop_words=None, ngram_range=(1, 1), lowercase=False),
    TfidfVectorizer(stop_words=None, ngram_range=(2, 2), lowercase=True),
    TfidfVectorizer(stop_words=None, ngram_range=(2, 2), lowercase=False)
]

# dfs = [df_sd[:200], df_te, df_ap, df_ai, df]
dfs = [df_sd[:200]]

results_svm = []
results_nb = []

print('LOOP DF START')
for i in range(len(dfs)):
    print('Loop df numero : {}'.format(i))
    results_df_svm = []
    results_df_nb = []

    print('LOOP VEC START')
    for idx, vec in enumerate(vecs):
        print('Loop vec numero : {}'.format(idx))
        print('======== LOOP NUMBER {} ========'.format(i*len(vecs) + idx))
        current_vec = vec
        X, y = current_vec.fit_transform(dfs[i]['text'].as_matrix()).toarray(), dfs[i]['sentiment'].as_matrix()
        parameters = {'kernel':('linear', 'rbf'), 'C':[0.01, 0.05, 0.1, 0.5, 1, 5]}

        # SVM
        print('SVM start')
        svr = svm.SVC()
        clf = GridSearchCV(svr, parameters)
        clf.fit(X, y)
        results_df_svm.append(clf.cv_results_)
        print('SVM finished')

        # Naive Bayes
        print('NB start')
        gnb = MultinomialNB()
        threshold = int(0.25*len(X))
        y_pred = gnb.fit(X[:threshold], y[:threshold]).predict(X[threshold:])
        target_names = ['negative', 'neutral', 'positive']
        results_df_nb.append(classification_report(y[threshold:], y_pred, target_names=target_names))
        print('NB finished')

    results_svm.append(results_df_svm)
    results_nb.append(results_df_nb)
    print('LOOP VEC FINISHED')

print('LOOP DF FINISHED')

print('Pickle started')
pickle.dump(results_svm, open( "results_svm.p", "wb" ) )
pickle.dump(results_nb, open( "results_nb.p", "wb" ) )
print('Pickle finished')

print('PROGRAM FINISHED')
