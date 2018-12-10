import numpy as np

def shadow(pixels, window, shadow_sub):

    subtract = lambda x: x - shadow_sub
    
    a, b, c = window[0], window[1], window[2]
    _pixels = np.copy(pixels)
    _pixels[0:a] = subtract(pixels[0:a])
    _pixels[a:b, c:] = subtract(_pixels[a:b, c:])
    _pixels[b:] = subtract(_pixels[b:])
    return _pixels
