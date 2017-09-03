"""Set of default paramters for different Radiance commands."""

rtrace_number_parameters = {
    'ambient_bounces': {'name': 'ab', 'dscrip': 'ambient bounces', 'type': int, 'default_value': 2, 'values': [2, 3, 6]},
    'ambient_divisions': {'name': 'ad', 'dscrip': 'ambient divisions', 'type': int, 'default_value': 512, 'values': [512, 2048, 4096]},
    'ambient_supersamples': {'name': 'as', 'dscrip': 'ambient super-samples', 'type': int, 'default_value': 128, 'values': [128, 2048, 4096]},
    'ambient_resolution': {'name': 'ar', 'dscrip': 'ambient resolution', 'type': int, 'default_value': 16, 'values': [16, 64, 128]},
    'ambient_accuracy': {'name': 'aa', 'dscrip': 'ambient accuracy', 'type': float, 'default_value': .25, 'values': [.25, .2, .1]},
    'direct_jitter': {'name': 'dj', 'dscrip': 'source jitter', 'type': float, 'default_value': 0, 'values': [0, .5, 1]},
    'direct_sampling': {'name': 'ds', 'dscrip': 'direct sampling', 'type': float, 'default_value': .5, 'values': [.5, .25, .05]},
    'direct_threshold': {'name': 'dt', 'dscrip': 'direct thresholding', 'type': float, 'default_value': .5, 'values': [.5, .25, .15]},
    'direct_certainty': {'name': 'dc', 'dscrip': 'direct certainty', 'type': float, 'default_value': .25, 'values': [.25, .5, .75]},
    'direct_sec_relays': {'name': 'dr', 'dscrip': 'direct relays', 'type': int, 'default_value': 0, 'values': [0, 1, 3]},
    'direct_presamp_density': {'name': 'dp', 'dscrip': 'direct pretest density', 'type': int, 'default_value': 64, 'values': [64, 256, 512]},
    'specular_threshold': {'name': 'st', 'dscrip': 'specular threshold', 'type': float, 'default_value': .85, 'values': [.85, .5, .15]},
    'limit_reflections': {'name': 'lr', 'dscrip': 'limit reflection', 'type': int, 'default_value': 4, 'values': [4, 6, 8]},
    'limit_weight': {'name': 'lw', 'dscrip': 'limit weight', 'type': float, 'default_value': .05, 'values': [.05, .01, .005]},
    'specular_sampling': {'name': 'ss', 'dscrip': 'specular sampling', 'type': float, 'default_value': 0, 'values': [0, .7, 1]}}

rtrace_boolean_parameters = {
    'irradiance_calc': {'name': 'I', 'dscrip': 'irradiance switch', 'type': bool, 'default_value': False, 'values': [False, False, False]},
    'uncor_rand_samp': {'name': 'u', 'dscrip': 'uncorrelated random sampling', 'type': bool, 'default_value': False, 'values': [False, False, False]}}

rpict_number_parameters = {
    'ambient_bounces': {'name': 'ab', 'dscrip': 'ambient bounces', 'type': int, 'default_value': 2, 'values': [2, 3, 6]},
    'ambient_divisions': {'name': 'ad', 'dscrip': 'ambient divisions', 'type': int, 'default_value': 512, 'values': [512, 2048, 4096]},
    'ambient_supersamples': {'name': 'as', 'dscrip': 'ambient super-samples', 'type': int, 'default_value': 128, 'values': [128, 2048, 4096]},
    'ambient_resolution': {'name': 'ar', 'dscrip': 'ambient resolution', 'type': int, 'default_value': 16, 'values': [16, 64, 128]},
    'ambient_accuracy': {'name': 'aa', 'dscrip': 'ambient accuracy', 'type': float, 'default_value': .25, 'values': [.25, .2, .1]},
    'pixel_sampling': {'name': 'ps', 'dscrip': 'pixel sampling rate', 'type': int, 'default_value': 8, 'values': [8, 4, 2]},
    'pixel_tolerance': {'name': 'pt', 'dscrip': 'sampling tolerance', 'type': float, 'default_value': .15, 'values': [.15, .10, .05]},
    'pixel_jitter': {'name': 'pj', 'dscrip': 'anti-aliasing jitter', 'type': float, 'default_value': .6, 'values': [.6, .9, .9]},
    'direct_jitter': {'name': 'dj', 'dscrip': 'source jitter', 'type': float, 'default_value': 0, 'values': [0, .5, 1]},
    'direct_sampling': {'name': 'ds', 'dscrip': 'direct sampling', 'type': float, 'default_value': .5, 'values': [.5, .25, .05]},
    'direct_threshold': {'name': 'dt', 'dscrip': 'direct thresholding', 'type': float, 'default_value': .5, 'values': [.5, .25, .15]},
    'direct_certainty': {'name': 'dc', 'dscrip': 'direct certainty', 'type': float, 'default_value': .25, 'values': [.25, .5, .75]},
    'direct_sec_relays': {'name': 'dr', 'dscrip': 'direct relays', 'type': int, 'default_value': 0, 'values': [0, 1, 3]},
    'direct_presamp_density': {'name': 'dp', 'dscrip': 'direct pretest density', 'type': int, 'default_value': 64, 'values': [64, 256, 512]},
    'specular_threshold': {'name': 'st', 'dscrip': 'specular threshold', 'type': float, 'default_value': .85, 'values': [.85, .5, .15]},
    'limit_reflections': {'name': 'lr', 'dscrip': 'limit reflection', 'type': int, 'default_value': 4, 'values': [4, 6, 8]},
    'limit_weight': {'name': 'lw', 'dscrip': 'limit weight', 'type': float, 'default_value': .05, 'values': [.05, .01, .005]},
    'specular_sampling': {'name': 'ss', 'dscrip': 'specular sampling', 'type': float, 'default_value': 0, 'values': [0, .7, 1]}}

rpict_boolean_parameters = {
    'uncor_rand_samp': {'name': 'u', 'dscrip': 'uncorrelated random sampling', 'type': bool, 'default_value': False, 'values': [False, False, False]}}
