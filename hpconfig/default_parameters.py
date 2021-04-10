def get_default_parameters (parameters):
    
    defaults = dict(early_stop=False, 
                  early_stop_metric='val_main_output_accuracy',
                  reduce_lr_on_plateau=True,
                  reduce_lr_metric='main_output_loss',
                  learning_rate = 0.0001,
                  epochs = 100,
                  batch_size = 512,
                  regularization=0.1,
                  target_recall=0.96,
                  min_recall=0.95,
                  max_recall=0.97,
                  architecture='big',
                  dropout_factor=1,
                  input_type='single',
                  gaussian_noise=0.005,
                  last_activation='sigmoid',
                  normal_sample_weight=0.1,
                  alert_sample_weight=0.6,
                  alarm_sample_weight=1.0,
                  normal_weight=0.1,
                  abnormal_weight=0.8,
                  reduce_lr_factor=0.2,
                  reduce_lr_patience=5)

    return defaults
