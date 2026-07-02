import streamlit as st
import numpy as np
from scipy.io import wavfile
from scipy import signal
import matplotlib.pyplot as plt
import io
import os
from pathlib import Path

# ==========================================
# CONFIGURAÇÃO: PASTA DE IMAGENS
# ==========================================
IMAGES_DIR = Path(__file__).parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

SAVE_DPI = 300

# Importando nossa camada de lógica matemática
import signal_processing as sp

st.set_page_config(page_title="Processador de Sinais LTI Avançado", layout="wide", initial_sidebar_state="expanded")
st.title("Analisador Avançado e Filtragem FIR de Áudio")

# ==========================================
# FUNÇÕES DE CACHE
# ==========================================

@st.cache_data
def load_and_process_audio(uploaded_file):
    """Lê o áudio e faz cache do vetor original para evitar reprocessamento."""
    fs, data = wavfile.read(uploaded_file)
    if len(data.shape) > 1:
        data = data.mean(axis=1)  # Converte estéreo para mono
    return fs, sp.normalize_signal(data)


@st.cache_data
def get_filter_design(fs, cutoff, filter_type, numtaps):
    """Projeta o filtro FIR e faz cache dos coeficientes h[n]."""
    return sp.design_fir_filter(fs, cutoff, filter_type, numtaps)


@st.cache_data
def process_filter(data, fs, cutoff, filter_type, numtaps):
    """Aplica o filtro FIR e faz cache do resultado pesado da convolução."""
    return sp.apply_fir_filter(data, fs, cutoff, filter_type, numtaps)


# ==========================================
# FUNÇÕES DE RENDERIZAÇÃO
# ==========================================

def save_figure(fig, filename):
    """Salva uma figura matplotlib na pasta images/ com alta resolução."""
    filepath = IMAGES_DIR / filename
    fig.savefig(filepath, dpi=SAVE_DPI, bbox_inches='tight')


def plot_spectrogram(data, fs):
    """Gera a Análise de Tempo-Frequência (STFT)."""
    fig, ax = plt.subplots(figsize=(10, 3))
    f, t, Sxx = signal.spectrogram(data, fs)
    cax = ax.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap='viridis')
    ax.set_ylabel('Frequência [Hz]')
    ax.set_xlabel('Tempo [s]')
    ax.set_title('Espectrograma (STFT)')
    fig.colorbar(cax, ax=ax, label='Intensidade [dB]')
    save_figure(fig, "espectrograma_stft.png")
    return fig


def plot_signal(x, y, title, xlabel, ylabel, save_filename=None, xlim=None):
    """Plota um sinal genérico no domínio do tempo ou frequência."""
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(x, y, color='#1f77b4', linewidth=0.8)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if xlim is not None:
        ax.set_xlim(xlim)
    ax.grid(True, linestyle='--', alpha=0.6)
    if save_filename:
        save_figure(fig, save_filename)
    return fig


def plot_frequency_response(taps, fs, cutoff, filter_type_slug):
    """
    Plota a resposta em frequência |H(ω)| em dB.
    Inclui marcadores de referência: linha de -3 dB (frequência de corte real)
    e linha vertical na frequência de corte projetada.
    """
    w, h_db = sp.compute_frequency_response(taps, fs)
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(w, h_db, color='#2ca02c', linewidth=1.2)
    ax.axhline(-3, color='red', linestyle='--', alpha=0.8, label='-3 dB (ponto de corte)')
    ax.axvline(cutoff, color='orange', linestyle='--', alpha=0.8, label=f'f_c projetada = {cutoff} Hz')
    ax.set_title('Resposta em Frequência do Filtro |H(ω)|')
    ax.set_xlabel('Frequência [Hz]')
    ax.set_ylabel('Magnitude [dB]')
    ax.set_ylim([-90, 5])
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    save_figure(fig, f"resposta_frequencia_filtro_{filter_type_slug}_{cutoff}hz.png")
    return fig


def plot_impulse_response(taps, filter_type_slug, cutoff):
    """
    Plota a resposta ao impulso discreta h[n] do filtro FIR.
    Para filtros FIR, os coeficientes do firwin são exatamente h[n].
    """
    n = np.arange(len(taps))
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.stem(n, taps, markerfmt='C1o', linefmt='C1-', basefmt='k-')
    ax.set_title('Resposta ao Impulso h[n]')
    ax.set_xlabel('Amostra [n]')
    ax.set_ylabel('Amplitude')
    ax.grid(True, linestyle='--', alpha=0.6)
    save_figure(fig, f"resposta_impulso_fir_{filter_type_slug}_{cutoff}hz.png")
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

        with st.sidebar:
            st.header("⚙️ Configurações de Visualização")
            nyquist = int(fs / 2)
            default_limit = min(8000, nyquist)
            max_freq_limit = st.slider(
                "Limite do Eixo X (FFT) [Hz]",
                min_value=1000,
                max_value=nyquist,
                value=default_limit,
                step=500,
                help="Ajusta o limite de frequência exibido nos gráficos de espectro FFT para focar nas faixas de maior energia."
            )
            st.caption(f"ℹ️ Frequência de Nyquist (máxima do áudio): **{nyquist} Hz**")

        # ---- Seção 1: Análise do Sinal Original ----
        st.subheader("1. Análise do Sinal Original")

        # Fix: resetar o ponteiro do arquivo após wavfile.read() para que
        # st.audio consiga ler o conteúdo corretamente.
        uploaded_file.seek(0)
        st.audio(uploaded_file, format='audio/wav')

        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(plot_signal(
                t, data,
                "Domínio do Tempo", "Tempo [s]", "Amplitude",
                save_filename="sinal_original_dominio_tempo.png"
            ))
        with col2:
            freqs, mag = sp.compute_fft(data, fs)
            st.pyplot(plot_signal(
                freqs, mag,
                "Domínio da Frequência (FFT)", "Frequência [Hz]", "Magnitude",
                save_filename="sinal_original_espectro_fft.png",
                xlim=(0, max_freq_limit)
            ))

        st.pyplot(plot_spectrogram(data, fs))

        st.markdown("---")

        # ---- Seção 2: Projeto do Filtro FIR ----
        st.subheader("2. Projeto de Filtro FIR (Janela de Hamming)")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_type = st.selectbox("Comportamento LTI", ["Passa-baixa", "Passa-alta"])
        with col_f2:
            cutoff = st.slider(
                "Frequência de Corte [Hz]",
                min_value=100,
                max_value=int(fs / 2 - 100),
                value=1000,
                step=100
            )
        with col_f3:
            numtaps = st.select_slider(
                "Ordem do Filtro (N° de coeficientes)",
                options=[51, 101, 151, 201, 251],
                value=101,
                help="Mais coeficientes = transição mais abrupta, mas maior custo computacional."
            )

        # Obtém os coeficientes h[n] do filtro projetado (cacheado separadamente)
        taps = get_filter_design(fs, cutoff, filter_type, numtaps)
        filter_type_slug = filter_type.lower().replace('-', '_').replace(' ', '_')

        col_fir1, col_fir2 = st.columns(2)
        with col_fir1:
            st.pyplot(plot_frequency_response(taps, fs, cutoff, filter_type_slug))
        with col_fir2:
            st.pyplot(plot_impulse_response(taps, filter_type_slug, cutoff))

        st.markdown("---")

        # ---- Seção 3: Resultado da Filtragem ----
        st.subheader("3. Resultado da Filtragem")

        filtered_data = process_filter(data, fs, cutoff, filter_type, numtaps)
        snr_value = sp.calculate_snr(data, filtered_data)

        st.info(
            f"**Filtro:** {filter_type} | "
            f"**Freq. de Corte:** {cutoff} Hz | "
            f"**N° de coeficientes:** {numtaps} | "
            f"**Índice de Preservação do Sinal:** {snr_value:.2f} dB"
        )

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.pyplot(plot_signal(
                t, filtered_data,
                f"Sinal Filtrado ({filter_type})", "Tempo [s]", "Amplitude",
                save_filename=f"sinal_filtrado_{filter_type_slug}_{cutoff}hz_dominio_tempo.png"
            ))
        with col_r2:
            f_freqs, f_mag = sp.compute_fft(filtered_data, fs)
            st.pyplot(plot_signal(
                f_freqs, f_mag,
                "Espectro Pós-Filtro", "Frequência [Hz]", "Magnitude",
                save_filename=f"sinal_filtrado_{filter_type_slug}_{cutoff}hz_espectro_fft.png",
                xlim=(0, max_freq_limit)
            ))

        # Fix: np.clip antes da conversão para int16 evita clipping silencioso
        # causado por transientes do filtfilt nas bordas do sinal.
        filtered_int16 = np.int16(np.clip(filtered_data, -1.0, 1.0) * 32767)
        virtual_file = io.BytesIO()
        wavfile.write(virtual_file, fs, filtered_int16)

        # getvalue() lê o buffer completo independente da posição do ponteiro
        audio_bytes = virtual_file.getvalue()

        st.audio(audio_bytes, format='audio/wav')

        filename = f"filtrado_{filter_type.lower().replace('-', '_')}_{cutoff}hz.wav"
        st.download_button(
            label="⬇️ Baixar Áudio Filtrado (.wav)",
            data=audio_bytes,
            file_name=filename,
            mime="audio/wav"
        )

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo. Detalhes: {e}")