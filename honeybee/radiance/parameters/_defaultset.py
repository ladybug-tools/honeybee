"""Set of default paramters for different Radiance commands."""

rtrace_number_parameters = {
    'ambientBounces': {'name': 'ab', 'dscrip': 'ambient bounces', 'type': int, 'default_value': 2, 'values': [2, 3, 6]},
    'ambientDivisions': {'name': 'ad', 'dscrip': 'ambient divisions', 'type': int, 'default_value': 512, 'values': [512, 2048, 4096]},
    'ambientSupersamples': {'name': 'as', 'dscrip': 'ambient super-samples', 'type': int, 'default_value': 128, 'values': [128, 2048, 4096]},
    'ambientResolution': {'name': 'ar', 'dscrip': 'ambient resolution', 'type': int, 'default_value': 16, 'values': [16, 64, 128]},
    'ambientAccuracy': {'name': 'aa', 'dscrip': 'ambient accuracy', 'type': float, 'default_value': .25, 'values': [.25, .2, .1]},
    'directJitter': {'name': 'dj', 'dscrip': 'source jitter', 'type': float, 'default_value': 0, 'values': [0, .5, 1]},
    'directSampling': {'name': 'ds', 'dscrip': 'direct sampling', 'type': float, 'default_value': .5, 'values': [.5, .25, .05]},
    'directThreshold': {'name': 'dt', 'dscrip': 'direct thresholding', 'type': float, 'default_value': .5, 'values': [.5, .25, .15]},
    'directCertainty': {'name': 'dc', 'dscrip': 'direct certainty', 'type': float, 'default_value': .25, 'values': [.25, .5, .75]},
    'directSecRelays': {'name': 'dr', 'dscrip': 'direct relays', 'type': int, 'default_value': 0, 'values': [0, 1, 3]},
    'directPresampDensity': {'name': 'dp', 'dscrip': 'direct pretest density', 'type': int, 'default_value': 64, 'values': [64, 256, 512]},
    'specularThreshold': {'name': 'st', 'dscrip': 'specular threshold', 'type': float, 'default_value': .85, 'values': [.85, .5, .15]},
    'limitReflections': {'name': 'lr', 'dscrip': 'limit reflection', 'type': int, 'default_value': 4, 'values': [4, 6, 8]},
    'limitWeight': {'name': 'lw', 'dscrip': 'limit weight', 'type': float, 'default_value': .05, 'values': [.05, .01, .005]},
    'specularSampling': {'name': 'ss', 'dscrip': 'specular sampling', 'type': float, 'default_value': 0, 'values': [0, .7, 1]}}

rtrace_boolean_parameters = {
    'irradiance_calc': {'name': 'I', 'dscrip': 'irradiance switch', 'type': bool, 'default_value': False, 'values': [False, False, False]},
    'uncorRandSamp': {'name': 'u', 'dscrip': 'uncorrelated random sampling', 'type': bool, 'default_value': False, 'values': [False, False, False]}}

rpict_number_parameters = {
    'ambientBounces': {'name': 'ab', 'dscrip': 'ambient bounces', 'type': int, 'default_value': 2, 'values': [2, 3, 6]},
    'ambientDivisions': {'name': 'ad', 'dscrip': 'ambient divisions', 'type': int, 'default_value': 512, 'values': [512, 2048, 4096]},
    'ambientSupersamples': {'name': 'as', 'dscrip': 'ambient super-samples', 'type': int, 'default_value': 128, 'values': [128, 2048, 4096]},
    'ambientResolution': {'name': 'ar', 'dscrip': 'ambient resolution', 'type': int, 'default_value': 16, 'values': [16, 64, 128]},
    'ambientAccuracy': {'name': 'aa', 'dscrip': 'ambient accuracy', 'type': float, 'default_value': .25, 'values': [.25, .2, .1]},
    'pixelSampling': {'name': 'ps', 'dscrip': 'pixel sampling rate', 'type': int, 'default_value': 8, 'values': [8, 4, 2]},
    'pixelTolerance': {'name': 'pt', 'dscrip': 'sampling tolerance', 'type': float, 'default_value': .15, 'values': [.15, .10, .05]},
    'pixelJitter': {'name': 'pj', 'dscrip': 'anti-aliasing jitter', 'type': float, 'default_value': .6, 'values': [.6, .9, .9]},
    'directJitter': {'name': 'dj', 'dscrip': 'source jitter', 'type': float, 'default_value': 0, 'values': [0, .5, 1]},
    'directSampling': {'name': 'ds', 'dscrip': 'direct sampling', 'type': float, 'default_value': .5, 'values': [.5, .25, .05]},
    'directThreshold': {'name': 'dt', 'dscrip': 'direct thresholding', 'type': float, 'default_value': .5, 'values': [.5, .25, .15]},
    'directCertainty': {'name': 'dc', 'dscrip': 'direct certainty', 'type': float, 'default_value': .25, 'values': [.25, .5, .75]},
    'directSecRelays': {'name': 'dr', 'dscrip': 'direct relays', 'type': int, 'default_value': 0, 'values': [0, 1, 3]},
    'directPresampDensity': {'name': 'dp', 'dscrip': 'direct pretest density', 'type': int, 'default_value': 64, 'values': [64, 256, 512]},
    'specularThreshold': {'name': 'st', 'dscrip': 'specular threshold', 'type': float, 'default_value': .85, 'values': [.85, .5, .15]},
    'limitReflections': {'name': 'lr', 'dscrip': 'limit reflection', 'type': int, 'default_value': 4, 'values': [4, 6, 8]},
    'limitWeight': {'name': 'lw', 'dscrip': 'limit weight', 'type': float, 'default_value': .05, 'values': [.05, .01, .005]},
    'specularSampling': {'name': 'ss', 'dscrip': 'specular sampling', 'type': float, 'default_value': 0, 'values': [0, .7, 1]}}

rpict_boolean_parameters = {
    'uncorRandSamp': {'name': 'u', 'dscrip': 'uncorrelated random sampling', 'type': bool, 'default_value': False, 'values': [False, False, False]}}
