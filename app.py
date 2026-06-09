import streamlit as st
import numpy as np
from scipy.io import wavfile
from scipy import signal
import matplotlib.pyplot as plt
import io

# Configuração da página
st.set_page_config(page_title="Processamento de Sinais de Áudio", layout="wide")
st.title("Analisador e Filtro de Sinais LTI")
st.write("Faça o upload de um arquivo .wav para analisar seu espectro e aplicar filtros digitais.")

# Função para plotar gráficos de forma otimizada
def plot_signal(t, sig, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(t, sig, color='#1f77b4')
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.6)
    return fig

# Upload do arquivo
uploaded_file = st.file_uploader("Escolha um arquivo de áudio (.wav)", type=["wav"])

if uploaded_file is not None:
    # Lendo o arquivo de áudio
    fs, data = wavfile.read(uploaded_file)
    
    # Convertendo para mono se for estéreo para simplificar a análise LTI
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    
    # Normalizando o sinal
    data = data / np.max(np.abs(data))
    
    # Vetor de tempo
    N = len(data)
    t = np.arange(N) / fs
    
    st.subheader("1. Sinal Original")
    st.audio(uploaded_file, format='audio/wav')
    st.pyplot(plot_signal(t, data, "Sinal no Domínio do Tempo", "Tempo [s]", "Amplitude"))
    
    # Análise de Fourier (FFT)
    st.subheader("2. Análise em Frequência (Transformada de Fourier)")
    
    # Calculando a FFT
    fft_data = np.fft.fft(data)
    fft_freq = np.fft.fftfreq(N, 1/fs)
    
    # Pegando apenas a parte positiva das frequências
    pos_mask = fft_freq > 0
    freqs_pos = fft_freq[pos_mask]
    fft_mag = np.abs(fft_data[pos_mask])
    
    st.pyplot(plot_signal(freqs_pos, fft_mag, "Espectro de Frequência", "Frequência [Hz]", "Magnitude"))
    
    # Projeto do Filtro LTI
    st.subheader("3. Filtragem LTI (Projeto de Filtro Butterworth)")
    
    col1, col2 = st.columns(2)
    with col1:
        filter_type = st.selectbox("Tipo de Filtro", ["Passa-baixa", "Passa-alta"])
    with col2:
        cutoff = st.slider("Frequência de Corte [Hz]", min_value=100, max_value=int(fs/2 - 100), value=1000, step=100)
    
    # Criando o filtro
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    btype = 'low' if filter_type == "Passa-baixa" else 'high'
    
    # Filtro Butterworth de ordem 4
    b, a = signal.butter(4, normal_cutoff, btype=btype, analog=False)
    
    # Aplicando o filtro (Convolução)
    # filtfilt aplica o filtro duas vezes (ida e volta) para ter fase linear (zero phase distortion)
    filtered_data = signal.filtfilt(b, a, data)
    
    st.pyplot(plot_signal(t, filtered_data, f"Sinal Filtrado ({filter_type} em {cutoff} Hz)", "Tempo [s]", "Amplitude"))
    
    # FFT do sinal filtrado para comparar
    fft_filtered = np.fft.fft(filtered_data)
    fft_mag_filtered = np.abs(fft_filtered[pos_mask])
    st.pyplot(plot_signal(freqs_pos, fft_mag_filtered, "Espectro do Sinal Filtrado", "Frequência [Hz]", "Magnitude"))
    
    # Disponibilizando o áudio filtrado para ouvir
    st.subheader("4. Resultado do Processamento")
    
    # Convertendo de volta para formato de áudio de 16 bits
    filtered_data_int16 = np.int16(filtered_data * 32767)
    virtual_file = io.BytesIO()
    wavfile.write(virtual_file, fs, filtered_data_int16)
    
    st.audio(virtual_file, format='audio/wav')