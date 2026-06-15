import numpy as np
from scipy import signal


def normalize_signal(data):
    """
    Normaliza a amplitude do sinal para o intervalo [-1, 1].
    Converte explicitamente para float64 antes da divisão para evitar
    comportamento inesperado com arrays de inteiros (int16, int32).
    """
    data = data.astype(np.float64)
    return data / np.max(np.abs(data))


def compute_fft(data, fs):
    """Calcula a Transformada Rápida de Fourier (FFT) e retorna frequências positivas."""
    N = len(data)
    fft_data = np.fft.fft(data)
    fft_freq = np.fft.fftfreq(N, 1 / fs)

    pos_mask = fft_freq > 0
    return fft_freq[pos_mask], np.abs(fft_data[pos_mask])


def design_fir_filter(fs, cutoff, filter_type, numtaps=101):
    """
    Projeta o filtro FIR com janela de Hamming e retorna os coeficientes h[n].
    Os coeficientes são a própria resposta ao impulso do sistema LTI.
    Separado de apply_fir_filter para permitir cache e visualização
    independentes do processo de filtragem.
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    pass_zero = 'lowpass' if filter_type == "Passa-baixa" else 'highpass'
    taps = signal.firwin(numtaps, normal_cutoff, window='hamming', pass_zero=pass_zero)
    return taps


def apply_fir_filter(data, fs, cutoff, filter_type, numtaps=101):
    """
    Aplica o filtro FIR ao sinal via filtfilt (filtragem de fase zero).
    O filtfilt aplica o filtro duas vezes (ida e volta) eliminando
    distorção de fase — importante para preservar a forma do sinal de áudio.
    Reutiliza design_fir_filter para manter o projeto centralizado.
    """
    taps = design_fir_filter(fs, cutoff, filter_type, numtaps)
    filtered_data = signal.filtfilt(taps, 1.0, data)
    return filtered_data


def compute_frequency_response(taps, fs):
    """
    Calcula a resposta em frequência H(ω) do filtro FIR em dB.
    Usa 8192 pontos para alta resolução espectral no eixo de frequência.
    Retorna: (frequências em Hz, magnitude em dB).
    """
    w, h = signal.freqz(taps, worN=8192, fs=fs)
    h_db = 20 * np.log10(np.abs(h) + 1e-10)
    return w, h_db


def calculate_snr(original, filtered):
    """
    Calcula o Índice de Preservação do Sinal (em dB).
    Trata a diferença entre original e filtrado como o conteúdo espectral removido.

    NOTA: Não representa o SNR tradicional (sinal vs. ruído de fundo captado),
    mas sim o quanto o filtro alterou o sinal original. Valores altos indicam
    que a filtragem preservou a maior parte do sinal; valores baixos indicam
    remoção intensa de conteúdo (esperado, p.ex., em passa-alta com f_c alta).
    """
    noise = original - filtered
    power_signal = np.mean(filtered ** 2)
    power_noise = np.mean(noise ** 2)

    if power_noise == 0:
        return float('inf')

    snr_db = 10 * np.log10(power_signal / power_noise)
    return snr_db