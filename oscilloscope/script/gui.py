import numpy as np
import dsp

# Empty array
EMPTY = np.array([])

# Time axis and frequency axis
TIME = {}
FREQ = {}
TIME[dsp.RAW_WAVE] = np.linspace(0, dsp.NUM_SAMPLES[dsp.RAW_WAVE]/dsp.Fs*1000.0, dsp.NUM_SAMPLES[dsp.RAW_WAVE])
FREQ[dsp.FFT] = np.linspace(0, dsp.Fs/2, dsp.NUM_SAMPLES[dsp.FFT])
TIME[dsp.SPECTROGRAM] = np.linspace(0, dsp.NUM_SAMPLES[dsp.RAW_WAVE]/dsp.Fs*200.0/2, 200)
FREQ[dsp.SPECTROGRAM] = np.linspace(0, dsp.Nyq, int(dsp.NN/2))
TIME[dsp.MEL_SPECTROGRAM] = np.linspace(-dsp.NUM_SAMPLES[dsp.RAW_WAVE]/dsp.Fs*200.0/2, 0, 200)
FREQ[dsp.MEL_SPECTROGRAM] = np.linspace(1, dsp.NUM_FILTERS+1, dsp.NUM_FILTERS)
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
    
    def __init__(self, interface):
        # Serial interface
        self.interface = interface

    # Use matplotlib to plot the output from the device
    def plot(self, ax, cmd, range_=None,
                 cmap=None, ssub=None,
                 window=None, data=EMPTY,
                 shadow_sub=0, remove_dc=False):

        if (data is EMPTY) and (cmd == dsp.MEL_SPECTROGRAM or cmd == dsp.MFCC):
            data = self.interface.read(dsp.FEATURES, ssub)
        elif data is EMPTY:
            data = self.interface.read(cmd, ssub)
            
        ax.clear()
        
        if cmd == dsp.RAW_WAVE:
            ax.set_title('Time domain')
            ax.plot(TIME[dsp.RAW_WAVE], data)
            ax.set_xlabel('Time [msec]')
            ax.set_ylabel('Amplitude')
            ax.set_ylim([-range_, range_])

        elif cmd == dsp.FFT:
            ax.set_title('Frequency domain')
            ax.plot(FREQ[dsp.FFT], data)
            ax.set_xlabel('Frequency [Hz]')
            ax.set_ylabel('PSD [dB]')
            ax.set_ylim([-8, 127])

        elif cmd == dsp.SPECTROGRAM:
            if window:
                shadowed = shadow(data, window, shadow_sub=10)
            else:
                shadowed = data          
            ax.pcolormesh(TIME[dsp.SPECTROGRAM],
                          FREQ[dsp.SPECTROGRAM][:range_],
                          shadowed.T[:range_],
                          cmap=cmap)
            ax.set_title('Spectrogram (PSD in dB)')
            ax.set_xlabel('Time [sec]')
            ax.set_ylabel('Frequency (Hz)')

        elif cmd == dsp.MEL_SPECTROGRAM:
            data_ = data[:200,:]
            if window:
                shadowed = shadow(data_, window, shadow_sub=10)
            else:
                shadowed = data_
            ax.pcolormesh(TIME[dsp.MEL_SPECTROGRAM],
                          FREQ[dsp.MEL_SPECTROGRAM][:range_],
                          shadowed.T[:range_],
                          cmap=cmap)
            ax.set_title('Mel-scale spectrogram (PSD in dB)')
            ax.set_xlabel('Time [sec]')
            ax.set_ylabel('Mel-scale filters')

        elif cmd == dsp.MFCC:
            data_ = data[200:,:]
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
            ax.set_title('MFCCs')
            ax.set_xlabel('Time [sec]')
            ax.set_ylabel('MFCC')     

        elif cmd == dsp.FILTERBANK: 
            data = data.reshape(dsp.NUM_FILTERS+2, dsp.FILTER_LENGTH)
            for m in range(1, dsp.NUM_FILTERS+1):
                num_axis = hz_freqs_n[m]+dsp.FILTER_LENGTH
                mel = np.zeros(num_axis)
                mel[hz_freqs_n[m]:hz_freqs_n[m]+dsp.FILTER_LENGTH] = data[m]
                ax.plot(mel)
                
            ax.set_title('Mel filter bank')
            ax.set_xlabel('n')
            ax.set_ylabel('Magnitude')

        return data

    def plot_welch(self, ax, data, window):
        data = data[window[0]:window[1], :window[2]]
        num_samples = window[1] - window[0]
        data = np.sum(data, axis=0)/num_samples
        ax.set_title("Welch's method")
        ax.stem(FREQ[dsp.FFT][:window[2]], data)
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('PSD [dB]')
        ax.set_ylim([-8, 127])
