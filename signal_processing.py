import numpy as np
from scipy import signal

def normalize_signal(data):
    """Normaliza a amplitude do sinal para evitar distorções (clipping)."""
    return data / np.max(np.abs(data))

def compute_fft(data, fs):
    """Calcula a Transformada Rápida de Fourier (FFT) e retorna frequências positivas."""
    N = len(data)
    fft_data = np.fft.fft(data)
    fft_freq = np.fft.fftfreq(N, 1/fs)
    
    pos_mask = fft_freq > 0
    return fft_freq[pos_mask], np.abs(fft_data[pos_mask])

def apply_fir_filter(data, fs, cutoff, filter_type, numtaps=101):
    """
    Aplica um filtro FIR projetado com janelamento de Hamming.
    O número de coeficientes (numtaps) define a ordem e a nitidez do filtro.
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    
    # Projeto do filtro FIR usando a janela de Hamming
    pass_zero = 'lowpass' if filter_type == "Passa-baixa" else 'highpass'
    taps = signal.firwin(numtaps, normal_cutoff, window='hamming', pass_zero=pass_zero)
    
    # Convolução do sinal com a resposta ao impulso do filtro
    filtered_data = signal.filtfilt(taps, 1.0, data)
    return filtered_data

def calculate_snr(original, filtered):
    """
    Calcula a Relação Sinal-Ruído (SNR) em dB.
    Considera a diferença entre o original e o filtrado como o ruído removido.
    """
    noise = original - filtered
    power_signal = np.mean(filtered ** 2)
    power_noise = np.mean(noise ** 2)
    
    # Evita divisão por zero
    if power_noise == 0:
        return float('inf')
        
    snr_db = 10 * np.log10(power_signal / power_noise)
    return snr_db