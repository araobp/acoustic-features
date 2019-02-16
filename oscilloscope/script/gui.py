import numpy as np
import dsp
from scipy.fftpack import dct

# Empty array
EMPTY = np.array([])

def shadow(pixels, window, shadow_sub):
    if window:
        subtract = lambda x: x - shadow_sub

        a, b, c = window[0], window[1], window[2]
        _pixels = np.copy(pixels)
        _pixels[0:a] = subtract(pixels[0:a])
        _pixels[a:b, c:] = subtract(_pixels[a:b, c:])
        _pixels[b:] = subtract(_pixels[b:])
    else:
        _pixels = pixels
    return _pixels

def spectrum_subtraction(data, ssub=None):
    data_ = np.copy(data)
    if ssub:
        data_ = data_ - ssub
        data_[data_ < 0] = 0
    return data_

# GUI class
class GUI:
    
    def __init__(self, interface, dataset, fullscreen=None):
        # Serial interface
        self.interface = interface
        self.filters = dataset.filters
        self.samples = dataset.samples
        self.fullscreen = True if fullscreen else False
        # Time axis and frequency axis
        self.time = {}
        self.freq = {}
        self.time[dsp.RAW_WAVE] = np.linspace(0, self.interface.num_samples[dsp.RAW_WAVE]/dsp.Fs*1000.0, self.interface.num_samples[dsp.RAW_WAVE])
        self.freq[dsp.FFT] = np.linspace(0, dsp.Fs/2, self.interface.num_samples[dsp.FFT])
        self.time[dsp.SPECTROGRAM] = np.linspace(0, self.interface.num_samples[dsp.RAW_WAVE]/dsp.Fs*self.samples/2, self.samples)
        self.freq[dsp.SPECTROGRAM] = np.linspace(0, dsp.Nyq, int(dsp.NN/2))
        self.time[dsp.MFSC] = np.linspace(-self.interface.num_samples[dsp.RAW_WAVE]/dsp.Fs*self.samples/2, 0, self.samples)
        self.freq[dsp.MFSC] = np.linspace(1, self.filters+1, self.filters)
        self.time[dsp.MFCC] = np.linspace(-self.interface.num_samples[dsp.RAW_WAVE]/dsp.Fs*self.samples/2, 0, self.samples)
        self.freq[dsp.MFCC] = np.linspace(0, self.filters, self.filters)

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
                 shadow_sub=0):

        if (data is EMPTY) and (cmd == dsp.MFSC or cmd == dsp.MFCC):
            data = self.interface.read(dsp.FEATURES)
        elif data is EMPTY:
            data = self.interface.read(cmd)
            
        ax.clear()
        
        if cmd == dsp.RAW_WAVE:
            ax.plot(self.time[dsp.RAW_WAVE], data)
            self.set_labels(ax, 'Time domain', 'Time [msec]', 'Amplitude', [-range_, range_])

        elif cmd == dsp.FFT:
            ax.plot(self.freq[dsp.FFT], data)
            self.set_labels(ax, 'Frequency domain', 'Frequency [Hz]', 'Power [dB]', [-70, 90])

        elif cmd == dsp.SPECTROGRAM:
            data_ = spectrum_subtraction(data, ssub)
            data_ = shadow(data_, window, shadow_sub=10)
            ax.pcolormesh(self.time[dsp.SPECTROGRAM],
                          self.freq[dsp.SPECTROGRAM][:range_],
                          data_.T[:range_],
                          cmap=cmap)
            self.set_labels(ax, 'Spectrogram', 'Time [sec]', 'Frequency (Hz)')

        elif cmd == dsp.MFSC:

            # Debug
            print('mfsc stm32: {}'.format(data[0]))
            print('mfcc stm32: {}'.format(data[self.samples]))

            data_ = spectrum_subtraction(data[:self.samples,:], ssub)
            data_ = shadow(data_, window, shadow_sub=10)
            ax.pcolormesh(self.time[dsp.MFSC],
                          self.freq[dsp.MFSC][:range_],
                          data_.T[:range_],
                          cmap=cmap)
            self.set_labels(ax, 'MFSCs', 'Time [sec]', 'MFSC')

        elif cmd == dsp.MFCC:
            
            # Debug
            print('mfsc stm32: {}'.format(data[0]))
            print('mfcc stm32: {}'.format(data[self.samples]))
            dcted = dct(data[0], norm='ortho').astype(int)
            dcted[0] = 0.0  # Remove DC
            print('mfcc python: {}'.format(dcted))

            data_ = spectrum_subtraction(data[self.samples:,:], ssub)
            data_ = shadow(data_, window, shadow_sub=10)
            ax.pcolormesh(self.time[dsp.MFCC],
                          self.freq[dsp.MFCC][:range_],
                          data_.T[:range_],
                          cmap=cmap)
            self.set_labels(ax, 'MFCCs', 'Time [sec]', 'MFCC')

        elif cmd == dsp.FILTERBANK:
            k_range, filterbank = data
            for m in range(1, self.filters+1):
                h = np.zeros(int(dsp.NN/2))
                k_left, len_ = k_range[m]
                h[k_left:k_left+len_] = filterbank[m][:len_]
                ax.plot(h)
            self.set_labels(ax, 'Mel filter bank', 'n', 'Magnitude')

        return data

    def plot_welch(self, ax):
        data = self.interface.read(dsp.SPECTROGRAM)
        ax.clear()

        data = np.sum(data, axis=0)/self.samples
        ax.plot(self.freq[dsp.FFT], data)
        self.set_labels(ax, "Welch's method", 'Frequency [Hz]', 'Power [dB]', [-70, 90])
