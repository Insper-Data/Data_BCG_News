import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import roc_auc_score, auc, roc_curve, brier_score_loss, average_precision_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
import copy
import datetime
import random
from boruta import BorutaPy


def boruta_select(X_df, Y, perc_list=[20], allowed_perc_good=.5, allowed_perc_med=.70, samples=[1], multiclass=False):
    """
    Runs the Boruta selector

    :param X_df: The X Dataframe that the selector will run on
    :param Y: The y for the training of the selector
    :param perc_list: The percentages that boruta will be run on
    :param allowed_perc_good: How many times does one variable has to beat the random ones
    :param allowed_perc_med: How many times does one variable has to be tentative
    :param samples: nothing at this moment, possible expansion into sampling
    :param multiclass: If problem is multiclass or not
    :return: first dataframe is if the varible should be used, second is what variables were relevant at each percentage
    , third is what variables were tentative in each percentage
    """

    use_list = []

    y = Y.values.ravel()

    res_df_good = pd.DataFrame(index=X_df.columns)
    res_df_med = pd.DataFrame(index=X_df.columns)
    use_df = pd.DataFrame(index=X_df.columns)
    if multiclass:
        params_bor = {'num_leaves': 20, 'n_estimators': 100, 'boosting_type': 'rf',
                      'bagging_fraction': .8, 'bagging_freq': 1}
    else:
        params_bor = {'num_leaves': 20, 'n_estimators': 100, 'boosting_type': 'rf',
                      'bagging_fraction': .8, 'bagging_freq': 1}

    rf_bor = lgb.LGBMClassifier(**params_bor)

    for perc_ in perc_list:
        print('Starting on {}'.format(perc_))
        feat_selector = BorutaPy(rf_bor, n_estimators=100, verbose=0, random_state=None, max_iter=10,
                                 perc=perc_)

        feat_selector.fit(X_df.values, y)
        if perc_ == perc_list[0]:
            times_good = (feat_selector.support_) * 1
            times_kinda_good = (feat_selector.support_weak_) * 1
        else:
            times_good += (feat_selector.support_) * 1
            times_kinda_good += (feat_selector.support_weak_) * 1

        res_df_good[str(perc_)] = (feat_selector.support_) * 1
        res_df_med[str(perc_)] = (feat_selector.support_weak_) * 1

    times_good_max = times_good.max()
    times_med_max = times_good.max()
    keep = (((times_good >= allowed_perc_good * times_good_max) |
             (times_kinda_good >= allowed_perc_med * times_med_max)) & (
        times_good + times_kinda_good > 0))

    # res_df_good[str(perc_)] = times_good
    # res_df_med[str(perc_)] = times_kinda_good
    use_df['use'] = keep

    # print(times_good_max, sum(keep))

    return (use_df, res_df_good, res_df_med)
