"""Set of default paramters for different Radiance commands."""

rtrace_number_parameters = {
    'ab': {'dscrip': 'ambient bounces', 'type': int, 'defaultValue': 2, 'values': [2, 3, 6]},
    'ad': {'dscrip': 'ambient divisions', 'type': int, 'defaultValue': 512, 'values': [512, 2048, 4096]},
    'as': {'dscrip': 'ambient super-samples', 'type': int, 'defaultValue': 128, 'values': [128, 2048, 4096]},
    'ar': {'dscrip': 'ambient resolution', 'type': int, 'defaultValue': 16, 'values': [16, 64, 128]},
    'aa': {'dscrip': 'ambient accuracy', 'type': float, 'defaultValue': .25, 'values': [.25, .2, .1]},
    'ds': {'dscrip': 'source substructuring', 'type': float, 'defaultValue': .5, 'values': [.5, .25, .05]},
    'dt': {'dscrip': 'direct thresholding', 'type': float, 'defaultValue': .5, 'values': [.5, .25, .15]},
    'dc': {'dscrip': 'direct certainty', 'type': float, 'defaultValue': .25, 'values': [.25, .5, .75]},
    'dr': {'dscrip': 'direct relays', 'type': int, 'defaultValue': 0, 'values': [0, 1, 3]},
    'dp': {'dscrip': 'direct pretest density', 'type': int, 'defaultValue': 64, 'values': [64, 256, 512]},
    'st': {'dscrip': 'specular threshold', 'type': float, 'defaultValue': .85, 'values': [.85, .5, .15]},
    'lr': {'dscrip': 'limit reflection', 'type': int, 'defaultValue': 4, 'values': [4, 6, 8]},
    'lw': {'dscrip': 'limit weight', 'type': float, 'defaultValue': .05, 'values': [.05, .01, .005]}}

rtrace_boolean_parameters = {
    'I': {'dscrip': 'irradiance switch', 'type': bool, 'defaultValue': False, 'values': [False, False, False]},
    'u': {'dscrip': 'uncorrelated random sampling', 'type': bool, 'defaultValue': False, 'values': [False, False, False]}}

rpict_number_parameters = {
    'ab': {'dscrip': 'ambient bounces', 'type': int, 'defaultValue': 2, 'values': [2, 3, 6]},
    'ad': {'dscrip': 'ambient divisions', 'type': int, 'defaultValue': 512, 'values': [512, 2048, 4096]},
    'as': {'dscrip': 'ambient super-samples', 'type': int, 'defaultValue': 128, 'values': [128, 2048, 4096]},
    'ar': {'dscrip': 'ambient resolution', 'type': int, 'defaultValue': 16, 'values': [16, 64, 128]},
    'aa': {'dscrip': 'ambient accuracy', 'type': float, 'defaultValue': .25, 'values': [.25, .2, .1]},
    'ps': {'dscrip': 'pixel sampling rate', 'type': int, 'defaultValue': 8, 'values': [8, 4, 2]},
    'pt': {'dscrip': 'sampling threshold', 'type': float, 'defaultValue': .15, 'values': [.15, .10, .05]},
    'pj': {'dscrip': 'anti-aliasing jitter', 'type': float, 'defaultValue': .6, 'values': [.6, .9, .9]},
    'dj': {'dscrip': 'source jitter', 'type': float, 'defaultValue': 0, 'values': [0, .5, .7]},
    'ds': {'dscrip': 'source substructuring', 'type': float, 'defaultValue': .5, 'values': [.5, .25, .05]},
    'dt': {'dscrip': 'direct thresholding', 'type': float, 'defaultValue': .5, 'values': [.5, .25, .15]},
    'dc': {'dscrip': 'direct certainty', 'type': float, 'defaultValue': .25, 'values': [.25, .5, .75]},
    'dr': {'dscrip': 'direct relays', 'type': int, 'defaultValue': 0, 'values': [0, 1, 3]},
    'dp': {'dscrip': 'direct pretest density', 'type': int, 'defaultValue': 64, 'values': [64, 256, 512]},
    'st': {'dscrip': 'specular threshold', 'type': float, 'defaultValue': .85, 'values': [.85, .5, .15]},
    'lr': {'dscrip': 'limit reflection', 'type': int, 'defaultValue': 4, 'values': [4, 6, 8]},
    'lw': {'dscrip': 'limit weight', 'type': float, 'defaultValue': .05, 'values': [.05, .01, .005]}}

rpict_boolean_parameters = {
    'u': {'dscrip': 'uncorrelated random sampling', 'type': bool, 'defaultValue': False, 'values': [False, False, False]}}
