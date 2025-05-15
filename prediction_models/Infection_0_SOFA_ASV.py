import sys
import numpy as np
import pandas as pd
import re
from PredictionPipelineV3 import *


merged_df_orig = pd.read_csv("/manitou/pmg/users/mc5672/post_processing_data/merged_df_orig_clr_ra.csv")

features = pd.read_csv("/manitou/pmg/users/mc5672/post_processing_data/unified_scrubbed_counts.csv",index_col=0).columns.to_list()

features += ['sofascore']

target = "infection"

# Filter for only day 0
merged_df_orig = merged_df_orig[merged_df_orig["sample"].str.contains("-D0", na=False)]

X = merged_df_orig[features]
X.columns = X.columns.str.replace(r'[^a-zA-Z0-9]', ' ', regex=True)  # remove JSON characters so that lightGBM can handle
y = merged_df_orig[[target, "id"]]
y = y.rename(columns={target: "outcome"})

run_params = {
    'steps': [
        ['CountFilter','VarianceFilter','FeatureSelector'],
	#['VarianceFilter','FeatureSelector'],

    ],
    #'preprocessing_method':[PreprocessingMethods.ABUN,PreprocessingMethods.CLR,PreprocessingMethods.LOG_RA],  # Done previously

    'feature_selection_method':[  # Each feature selection method has specific parameters defined for it in PipelineSteps/FeatureSelector.py 
        [FeatureSelectionMethods.UNIVAR,FeatureSelectionMethods.LASSO], # You can stack feature selection  methods!
        [FeatureSelectionMethods.UNIVAR], 
        [FeatureSelectionMethods.LASSO], 
    ],
    
    'count_filter_threshold': [0,1,5,8],
    'count_filter_num_samples': [0,0.01,0.05,0.1],
    
    'univar_score_func': ['f'],
    'univar_mode': ['k_best'],
    'univar_param': [0.01,0.05,0.1,0.25,0.5,0.75,-1],
    
    'lasso_k': [0.05,0.1,0.25],
}
model_params_gbm = Defaults.LIGHTGBM_NEW
model_params_gbm['is_unbalance'] = True  # Address class imbalance
model_params_gbm['n_estimators'] = [100, 200, 300, 500, 1000]

model_params_logit = {
    'penalty': ['l1','l2'],
    'solver': ['liblinear','saga'],
    'class_weight':['balanced'],
}


RUN_NAME = 'infection_0_sofaasv_nested_logit'
pred = Prediction(
    X=X,
    md=y,
    run_name=RUN_NAME,
    model_type=ModelType.LOGISTIC,  # ModelType.LOGISTIC ModelType.LIGHTGBM
    run_hp_space=run_params,
    model_hp_space=model_params_logit, # model_params_logit model_params_gbm
)

pred.run(
    target_col='outcome', # Target column in your `y` dataframe
    outer_folds=10,
    inner_folds=5,
    robust=3,
    iterations=1000, # 1000
    stratified=True,
    group_by = 'id',
    use_smart_hp_sampler=True,
    on_cluster=True, # Set this to `True` if running on manitou
    n_jobs=30, # 50
    seed = 42,
    cpus = 2,
    hours = 36,
    mem = '24G',
    stagger_seconds=30, 
    tryrerun=True, 
    add_name_suffix_to_file=True,
    out_file=f'preds_new/{RUN_NAME}.pkl',
    conda_env='Aya_pp3',
    #out_dir='/manitou/pmg/users/mc5672/pp3',
    dry_run=False, # You can set `dry_run` to True if you don't actually want to run the prediction yet
    log=False
)
