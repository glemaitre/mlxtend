# Sebastian Raschka 2014-2016
# mlxtend Machine Learning Library Extensions
# Author: Sebastian Raschka <sebastianraschka.com>
#
# License: BSD 3 clause

from mlxtend.classifier import StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from sklearn import datasets
from mlxtend.utils import assert_raises
from nose.tools import assert_almost_equal
from distutils.version import LooseVersion as Version
from sklearn import __version__ as sklearn_version
if Version(sklearn_version) < '0.18':
    from sklearn.grid_search import GridSearchCV
    from sklearn.cross_validation import cross_val_score
    from sklearn.utils.validation import NotFittedError
else:
    from sklearn.model_selection import GridSearchCV
    from sklearn.model_selection import cross_val_score
    from sklearn.exceptions import NotFittedError


iris = datasets.load_iris()
X, y = iris.data[:, 1:3], iris.target


def test_StackingClassifier():
    np.random.seed(123)
    meta = LogisticRegression()
    clf1 = RandomForestClassifier()
    clf2 = GaussianNB()
    sclf = StackingClassifier(classifiers=[clf1, clf2],
                              meta_classifier=meta)

    scores = cross_val_score(sclf,
                             X,
                             y,
                             cv=5,
                             scoring='accuracy')
    scores_mean = (round(scores.mean(), 2))
    assert scores_mean == 0.95


def test_StackingClassifier_proba_avg_1():

    np.random.seed(123)
    meta = LogisticRegression()
    clf1 = RandomForestClassifier()
    clf2 = GaussianNB()
    sclf = StackingClassifier(classifiers=[clf1, clf2],
                              use_probas=True,
                              meta_classifier=meta)

    scores = cross_val_score(sclf,
                             X,
                             y,
                             cv=5,
                             scoring='accuracy')
    scores_mean = (round(scores.mean(), 2))
    assert scores_mean == 0.93, scores_mean


def test_StackingClassifier_proba_concat_1():

    np.random.seed(123)
    meta = LogisticRegression()
    clf1 = RandomForestClassifier()
    clf2 = GaussianNB()
    sclf = StackingClassifier(classifiers=[clf1, clf2],
                              use_probas=True,
                              average_probas=False,
                              meta_classifier=meta)

    scores = cross_val_score(sclf,
                             X,
                             y,
                             cv=5,
                             scoring='accuracy')
    scores_mean = (round(scores.mean(), 2))
    assert scores_mean == 0.93, scores_mean


def test_StackingClassifier_avg_vs_concat():
    np.random.seed(123)
    lr1 = LogisticRegression()
    sclf1 = StackingClassifier(classifiers=[lr1, lr1],
                               use_probas=True,
                               average_probas=True,
                               meta_classifier=lr1)

    sclf1.fit(X, y)
    r1 = sclf1._predict_meta_features(X[:2])
    assert r1.shape == (2, 3)
    assert_almost_equal(np.sum(r1[0]), 1.0, places=6)
    assert_almost_equal(np.sum(r1[1]), 1.0, places=6)

    sclf2 = StackingClassifier(classifiers=[lr1, lr1],
                               use_probas=True,
                               average_probas=False,
                               meta_classifier=lr1)

    sclf2.fit(X, y)
    r2 = sclf2._predict_meta_features(X[:2])
    assert r2.shape == (2, 6)
    assert_almost_equal(np.sum(r2[0]), 2.0, places=6)
    assert_almost_equal(np.sum(r2[1]), 2.0, places=6)
    np.array_equal(r2[0][:3], r2[0][3:])


def test_gridsearch():
    np.random.seed(123)
    meta = LogisticRegression()
    clf1 = RandomForestClassifier()
    clf2 = GaussianNB()
    sclf = StackingClassifier(classifiers=[clf1, clf2],
                              meta_classifier=meta)

    params = {'meta-logisticregression__C': [1.0, 100.0],
              'randomforestclassifier__n_estimators': [20, 200]}

    grid = GridSearchCV(estimator=sclf, param_grid=params, cv=5)
    grid.fit(iris.data, iris.target)

    if Version(sklearn_version) < '0.18':
        mean_scores = []
        for params, mean_score, scores in grid.grid_scores_:
            mean_scores.append(round(mean_score, 2))
    else:
        mean_scores = [round(s, 2) for s
                       in grid.cv_results_['mean_test_score']]

    assert mean_scores == [0.95, 0.97, 0.96, 0.96]


def test_gridsearch_enumerate_names():
    np.random.seed(123)
    meta = LogisticRegression()
    clf1 = RandomForestClassifier()
    clf2 = GaussianNB()
    sclf = StackingClassifier(classifiers=[clf1, clf1, clf2],
                              meta_classifier=meta)

    params = {'meta-logisticregression__C': [1.0, 100.0],
              'randomforestclassifier-1__n_estimators': [5, 10],
              'randomforestclassifier-2__n_estimators': [5, 20]}

    grid = GridSearchCV(estimator=sclf, param_grid=params, cv=5)
    grid = grid.fit(iris.data, iris.target)


def test_use_probas():
    np.random.seed(123)
    meta = LogisticRegression()
    clf1 = RandomForestClassifier()
    clf2 = GaussianNB()
    sclf = StackingClassifier(classifiers=[clf1, clf2],
                              use_probas=True,
                              meta_classifier=meta)

    scores = cross_val_score(sclf,
                             X,
                             y,
                             cv=5,
                             scoring='accuracy')
    scores_mean = (round(scores.mean(), 2))
    assert scores_mean == 0.93, scores_mean


def test_not_fitted():
    np.random.seed(123)
    meta = LogisticRegression()
    clf1 = RandomForestClassifier()
    clf2 = GaussianNB()
    sclf = StackingClassifier(classifiers=[clf1, clf2],
                              use_probas=True,
                              meta_classifier=meta)

    assert_raises(NotFittedError,
                  "This StackingClassifier instance is not fitted yet."
                  " Call 'fit' with appropriate arguments"
                  " before using this method.",
                  sclf.predict,
                  iris.data)

    assert_raises(NotFittedError,
                  "This StackingClassifier instance is not fitted yet."
                  " Call 'fit' with appropriate arguments"
                  " before using this method.",
                  sclf.predict_proba,
                  iris.data)


def test_verbose():
    np.random.seed(123)
    meta = LogisticRegression()
    clf1 = RandomForestClassifier()
    clf2 = GaussianNB()
    sclf = StackingClassifier(classifiers=[clf1, clf2],
                              use_probas=True,
                              meta_classifier=meta,
                              verbose=3)
    sclf.fit(iris.data, iris.target)
