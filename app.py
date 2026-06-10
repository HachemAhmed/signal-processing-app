import streamlit as st
import numpy as np
from scipy.io import wavfile
from scipy import signal
import matplotlib.pyplot as plt
import io

# Importando nossa camada de lógica matemática
import signal_processing as sp

st.set_page_config(page_title="Processador de Sinais LTI Avançado", layout="wide")
st.title("Analisador Avançado e Filtragem FIR de Áudio")

# ==========================================
# FUNÇÕES DE CACHE E RENDERIZAÇÃO
# ==========================================

@st.cache_data
def load_and_process_audio(uploaded_file):
    """Lê o áudio e faz cache do vetor original para evitar reprocessamento."""
    fs, data = wavfile.read(uploaded_file)
    if len(data.shape) > 1:
        data = data.mean(axis=1) # Converte estéreo para mono
    return fs, sp.normalize_signal(data)

@st.cache_data
def process_filter(data, fs, cutoff, filter_type):
    """Aplica o filtro FIR e faz cache do resultado pesado da convolução."""
    return sp.apply_fir_filter(data, fs, cutoff, filter_type)

def plot_spectrogram(data, fs):
    """Gera a Análise de Tempo-Frequência (STFT)."""
    fig, ax = plt.subplots(figsize=(10, 3))
    f, t, Sxx = signal.spectrogram(data, fs)
    cax = ax.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
    ax.set_ylabel('Frequência [Hz]')
    ax.set_xlabel('Tempo [s]')
    ax.set_title('Espectrograma (STFT)')
    fig.colorbar(cax, ax=ax, label='Intensidade [dB]')
    return fig

def plot_signal(x, y, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(x, y, color='#1f77b4', linewidth=0.8)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.6)
    return fig

# ==========================================
# FLUXO PRINCIPAL (INTERFACE)
# ==========================================

uploaded_file = st.file_uploader("Suba um arquivo de áudio (.wav)", type=["wav"])

if uploaded_file is not None:
    try:
        fs, data = load_and_process_audio(uploaded_file)
        N = len(data)
        t = np.arange(N) / fs
        
        st.subheader("1. Análise do Sinal Original")
        st.audio(uploaded_file, format='audio/wav')
        
        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(plot_signal(t, data, "Domínio do Tempo", "Tempo [s]", "Amplitude"))
        with col2:
            freqs, mag = sp.compute_fft(data, fs)
            st.pyplot(plot_signal(freqs, mag, "Domínio da Frequência (FFT)", "Frequência [Hz]", "Magnitude"))
            
        st.pyplot(plot_spectrogram(data, fs))

        st.markdown("---")
        st.subheader("2. Projeto de Filtro FIR (Janela de Hamming)")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_type = st.selectbox("Comportamento LTI", ["Passa-baixa", "Passa-alta"])
        with col_f2:
            cutoff = st.slider("Frequência de Corte [Hz]", min_value=100, max_value=int(fs/2 - 100), value=1000, step=100)
        
        # Chamando a função cacheada da convolução
        filtered_data = process_filter(data, fs, cutoff, filter_type)
        
        # Calculando as métricas de performance
        snr_value = sp.calculate_snr(data, filtered_data)
        
        st.success(f"Filtragem concluída! SNR (Relação Sinal-Ruído): **{snr_value:.2f} dB**")
        
        st.subheader("3. Resultado da Filtragem")
        col_r1, col_r2 = st.columns(2)
        
        with col_r1:
            st.pyplot(plot_signal(t, filtered_data, f"Sinal Filtrado ({filter_type})", "Tempo [s]", "Amplitude"))
        with col_r2:
            f_freqs, f_mag = sp.compute_fft(filtered_data, fs)
            st.pyplot(plot_signal(f_freqs, f_mag, "Espectro Pós-Filtro", "Frequência [Hz]", "Magnitude"))

        # Disponibilizando o áudio final
        filtered_int16 = np.int16(filtered_data * 32767)
        virtual_file = io.BytesIO()
        wavfile.write(virtual_file, fs, filtered_int16)
        
        st.audio(virtual_file, format='audio/wav')

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo. Detalhes: {e}")