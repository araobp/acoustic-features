import numpy as np
import dsp
from scipy.fftpack import dct

# Empty array
EMPTY = np.array([])

# Time axis and frequency axis
TIME = {}
FREQ = {}
TIME[dsp.RAW_WAVE] = np.linspace(0, dsp.NUM_SAMPLES[dsp.RAW_WAVE]/dsp.Fs*1000.0, dsp.NUM_SAMPLES[dsp.RAW_WAVE])
FREQ[dsp.FFT] = np.linspace(0, dsp.Fs/2, dsp.NUM_SAMPLES[dsp.FFT])
TIME[dsp.SPECTROGRAM] = np.linspace(0, dsp.NUM_SAMPLES[dsp.RAW_WAVE]/dsp.Fs*200.0/2, 200)
FREQ[dsp.SPECTROGRAM] = np.linspace(0, dsp.Nyq, int(dsp.NN/2))
TIME[dsp.MFSC] = np.linspace(-dsp.NUM_SAMPLES[dsp.RAW_WAVE]/dsp.Fs*200.0/2, 0, 200)
FREQ[dsp.MFSC] = np.linspace(1, dsp.NUM_FILTERS+1, dsp.NUM_FILTERS)
TIME[dsp.MFCC] = np.linspace(-dsp.NUM_SAMPLES[dsp.RAW_WAVE]/dsp.Fs*200.0/2, 0, 200)
FREQ[dsp.MFCC] = np.linspace(0, dsp.NUM_FILTERS, dsp.NUM_FILTERS)

# Convert frequency to Mel
def hz2mel(hz):
  return 2595.0 * np.log10(hz/700.0 + 1.0);

# Convert Mel to frequency
def mel2hz(mel):
  return 700.0 * (10.0**(mel/2595.0) - 1.0);

# Convert n to frequency
def n2hz(n):
  return float(n)/dsp.NN * nyq_fs

hz_freqs = np.zeros(dsp.NUM_FILTERS+2)
hz_freqs_n = np.zeros(dsp.NUM_FILTERS+2, dtype=int)
mel_delta = hz2mel(dsp.Nyq)/(dsp.NUM_FILTERS+2)

for m in range(0, dsp.NUM_FILTERS+2):
    hz_freqs[m] = mel2hz(mel_delta * m)
    hz_freqs_n[m] = (int)(hz_freqs[m] / dsp.Nyq * dsp.NN / 2)

def shadow(pixels, window, shadow_sub):

    subtract = lambda x: x - shadow_sub
    
    a, b, c = window[0], window[1], window[2]
    _pixels = np.copy(pixels)
    _pixels[0:a] = subtract(pixels[0:a])
    _pixels[a:b, c:] = subtract(_pixels[a:b, c:])
    _pixels[b:] = subtract(_pixels[b:])
    return _pixels

# GUI class
class GUI:
    
    def __init__(self, interface, fullscreen=None):
        # Serial interface
        self.interface = interface
        self.fullscreen = True if fullscreen else False

    def set_labels(self, ax, title, xlabel, ylabel, ylim=None):
        if self.fullscreen:
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
        if ylim:
            ax.set_ylim(ylim)

    # Use matplotlib to plot the output from the device
    def plot(self, ax, cmd, range_=None,
                 cmap=None, ssub=None,
                 window=None, data=EMPTY,
                 shadow_sub=0, remove_dc=False):

        if (data is EMPTY) and (cmd == dsp.MFSC or cmd == dsp.MFCC):
            data = self.interface.read(dsp.FEATURES, ssub)
        elif data is EMPTY:
            data = self.interface.read(cmd, ssub)
            
        ax.clear()
        
        if cmd == dsp.RAW_WAVE:
            ax.plot(TIME[dsp.RAW_WAVE], data)
            self.set_labels(ax, 'Time domain', 'Time [msec]', 'Amplitude', [-range_, range_])

        elif cmd == dsp.FFT:
            ax.plot(FREQ[dsp.FFT], data)
            self.set_labels(ax, 'Frequency domain', 'Frequency [Hz]', 'Power [dB]', [-128, 90])

        elif cmd == dsp.SPECTROGRAM:
            if window:
                shadowed = shadow(data, window, shadow_sub=10)
            else:
                shadowed = data          
            ax.pcolormesh(TIME[dsp.SPECTROGRAM],
                          FREQ[dsp.SPECTROGRAM][:range_],
                          shadowed.T[:range_],
                          cmap=cmap)
            self.set_labels(ax, 'Spectrogram', 'Time [sec]', 'Frequency (Hz)')

        elif cmd == dsp.MFSC:
            data_ = data[:200,:]
            print('MFSC max abs: {}'.format(np.max(np.abs(data_))))
            if window:
                shadowed = shadow(data_, window, shadow_sub=10)
            else:
                shadowed = data_
            if remove_dc:
                ax.pcolormesh(TIME[dsp.MFSC],
                          FREQ[dsp.MFSC][1:range_],
                          shadowed.T[1:range_],
                          cmap=cmap)                
            else:
                ax.pcolormesh(TIME[dsp.MFSC],
                          FREQ[dsp.MFSC][:range_],
                          shadowed.T[:range_],
                          cmap=cmap)
            self.set_labels(ax, 'MFSCs', 'Time [sec]', 'MFSC')

        elif cmd == dsp.MFCC:
            # Debug
            print('mfsc: {}'.format(data[0]))
            print('mfcc stm32: {}'.format(data[200][1:]))
            print('mfcc python: {}'.format(dct(data[0]/10.0).astype(int)[1:]))
            data_ = data[200:,:]
            print('MFCC max abs: {}'.format(np.max(np.abs(data_[:,1:]))))
            if window:
                shadowed = shadow(data_, window, shadow_sub=10)
            else:
                shadowed = data_
            if remove_dc:
                ax.pcolormesh(TIME[dsp.MFCC],
                          FREQ[dsp.MFCC][1:range_],
                          shadowed.T[1:range_],
                          cmap=cmap)                
            else:
                ax.pcolormesh(TIME[dsp.MFCC],
                          FREQ[dsp.MFCC][:range_],
                          shadowed.T[:range_],
                          cmap=cmap)
            self.set_labels(ax, 'MFCCs', 'Time [sec]', 'MFCC')

        elif cmd == dsp.FILTERBANK:
            k_range, filterbank = data
            for m in range(1, dsp.NUM_FILTERS+1):
                h = np.zeros(int(dsp.NN/2))
                k_left, len = k_range[m]
                h[k_left:k_left+len] = filterbank[m][:len]
                ax.plot(h)
            self.set_labels(ax, 'Mel filter ban k', 'n', 'Magnitude')

        return data

    def plot_welch(self, ax):
        data = self.interface.read(dsp.SPECTROGRAM)
        ax.clear()

        data = np.sum(data, axis=0)/(dsp.NN/2)
        ax.plot(FREQ[dsp.FFT], data)
        self.set_labels(ax, "Welch's method", 'Frequency [Hz]', 'Power [dB]', [-128, 90])
