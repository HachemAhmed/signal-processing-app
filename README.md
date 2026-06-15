# 🎛️ Analisador Avançado e Filtragem FIR de Áudio

Aplicação web interativa para **análise espectral** e **filtragem digital FIR** de sinais de áudio, construída com Streamlit e fundamentada em conceitos de **Sistemas Lineares e Invariantes no Tempo (LTI)**.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Fundamentos Teóricos](#-fundamentos-teóricos)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação e Execução](#-instalação-e-execução)
- [Como Usar](#-como-usar)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Referência Técnica das Funções](#-referência-técnica-das-funções)
- [Pipeline de Processamento](#-pipeline-de-processamento)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Licença](#-licença)

---

## 🔍 Visão Geral

Esta aplicação permite ao usuário:

1. **Carregar** um arquivo de áudio no formato `.wav`.
2. **Visualizar** o sinal no domínio do tempo e no domínio da frequência (via FFT).
3. **Analisar** o espectrograma (STFT) para compreender a distribuição tempo-frequência.
4. **Projetar e aplicar** filtros digitais FIR (Passa-baixa ou Passa-alta) com janela de Hamming.
5. **Comparar** o sinal original com o sinal filtrado, tanto no domínio do tempo quanto no da frequência.
6. **Ouvir** o resultado da filtragem diretamente no navegador.
7. **Avaliar** a qualidade da filtragem por meio da métrica **SNR (Relação Sinal-Ruído)** em dB.

---

## 📐 Fundamentos Teóricos

### Sistemas LTI (Lineares e Invariantes no Tempo)

Um sistema LTI é um sistema que satisfaz duas propriedades fundamentais:

- **Linearidade (Superposição):** A resposta a uma combinação linear de entradas é a mesma combinação linear das respostas individuais.
- **Invariância no Tempo:** Um deslocamento temporal na entrada causa o mesmo deslocamento na saída, sem alterar sua forma.

Os filtros FIR implementados nesta aplicação são exemplos clássicos de sistemas LTI, onde a saída é obtida pela **convolução** da entrada com a resposta ao impulso do filtro.

### Transformada Rápida de Fourier (FFT)

A FFT é um algoritmo eficiente para calcular a **Transformada Discreta de Fourier (DFT)**, que decompõe um sinal no domínio do tempo em suas componentes de frequência:

$$X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-j \cdot 2\pi \cdot k \cdot n / N}$$

Onde:
- `x[n]` é o sinal no domínio do tempo.
- `X[k]` é o espectro de frequência.
- `N` é o número total de amostras.

A aplicação exibe apenas as **frequências positivas**, pois para sinais reais o espectro é simétrico (conjugado).

### Filtro FIR (Finite Impulse Response)

Um filtro FIR possui uma resposta ao impulso de duração finita. A saída é calculada por:

$$y[n] = \sum_{k=0}^{M-1} h[k] \cdot x[n-k]$$

Onde:
- `h[k]` são os coeficientes (taps) do filtro.
- `M` é a ordem do filtro (número de coeficientes).
- A operação é uma **convolução discreta**.

**Vantagens dos filtros FIR:**
- Sempre estáveis (todos os polos na origem).
- Podem ter fase linear exata (simetria dos coeficientes).
- Projeto mais simples e previsível.

### Janela de Hamming

O projeto do filtro utiliza a **janela de Hamming** para suavizar os coeficientes e reduzir o efeito de ripple (ondulações) na banda de rejeição:

$$w[n] = 0.54 - 0.46 \cdot \cos\left(\frac{2\pi n}{M-1}\right)$$

### Espectrograma (STFT)

O espectrograma é obtido pela **Short-Time Fourier Transform (STFT)**, que aplica a FFT em janelas deslizantes ao longo do sinal, revelando como as frequências variam ao longo do tempo.

### Relação Sinal-Ruído (SNR)

A SNR quantifica a eficácia da filtragem, medida em decibéis (dB):

$$\text{SNR}_{dB} = 10 \cdot \log_{10}\left(\frac{P_{\text{sinal}}}{P_{\text{ruído}}}\right)$$

Onde:
- `P_sinal` = potência média do sinal filtrado.
- `P_ruído` = potência média da diferença entre o sinal original e o filtrado (ruído removido).

Um valor alto de SNR indica que o filtro preservou a maior parte da energia útil do sinal.

---

## 🏗️ Arquitetura do Sistema

A aplicação segue uma arquitetura em **duas camadas** com separação clara de responsabilidades:

```
┌─────────────────────────────────────────────────────┐
│                   app.py (Camada UI)                │
│  ┌───────────────┐  ┌────────────┐  ┌────────────┐ │
│  │  Upload .wav   │  │  Controles │  │ Visualização│ │
│  │  st.file_uplo- │  │  Sliders & │  │ Matplotlib  │ │
│  │  ader()        │  │  Selectbox │  │ + st.audio  │ │
│  └───────┬───────┘  └─────┬──────┘  └──────▲─────┘ │
│          │                │                 │       │
│          │    ┌───────────▼─────────┐       │       │
│          │    │  Cache (st.cache)   │       │       │
│          │    └───────────┬─────────┘       │       │
└──────────┼────────────────┼─────────────────┼───────┘
           │                │                 │
           ▼                ▼                 │
┌─────────────────────────────────────────────┼───────┐
│        signal_processing.py (Camada Lógica) │       │
│  ┌────────────────┐  ┌──────────────────┐   │       │
│  │normalize_signal│  │  apply_fir_filter │───┘       │
│  │  compute_fft   │  │  calculate_snr   │           │
│  └────────────────┘  └──────────────────┘           │
│              NumPy + SciPy                          │
└─────────────────────────────────────────────────────┘
```

| Camada | Arquivo | Responsabilidade |
|---|---|---|
| **Interface (UI)** | `app.py` | Upload de arquivos, controles interativos, renderização de gráficos e reprodução de áudio |
| **Lógica Matemática** | `signal_processing.py` | Normalização, FFT, projeto de filtros FIR, convolução e cálculo de SNR |

---

## ✅ Pré-requisitos

- **Python** 3.8 ou superior
- **pip** (gerenciador de pacotes Python)
- Um navegador web moderno (Chrome, Firefox, Edge, Safari)

---

## 🚀 Instalação e Execução

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/signal-processing-app.git
cd signal-processing-app
```

### 2. Criar e ativar ambiente virtual (recomendado)

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação

```bash
streamlit run app.py
```

A aplicação será iniciada e abrirá automaticamente no navegador em `http://localhost:8501`.

---

## 🖥️ Como Usar

### Passo 1 — Carregar o áudio
Clique em **"Browse files"** e selecione um arquivo `.wav`. A aplicação aceita arquivos mono ou estéreo (estéreo é convertido automaticamente para mono).

### Passo 2 — Analisar o sinal original
Após o upload, a aplicação exibe automaticamente:
- **Gráfico Temporal:** Amplitude × Tempo do sinal completo.
- **Gráfico Espectral (FFT):** Magnitude × Frequência, mostrando as componentes de frequência presentes.
- **Espectrograma (STFT):** Mapa de calor mostrando a evolução das frequências ao longo do tempo.

### Passo 3 — Projetar o filtro
Configure os parâmetros do filtro FIR:
- **Tipo:** `Passa-baixa` (atenua frequências acima do corte) ou `Passa-alta` (atenua frequências abaixo do corte).
- **Frequência de Corte:** Ajuste com o slider (100 Hz até `fs/2 - 100` Hz).

### Passo 4 — Avaliar o resultado
A aplicação exibe:
- O valor de **SNR** em dB (qualidade da filtragem).
- Gráficos do sinal filtrado no domínio do tempo e da frequência.
- O **áudio filtrado**, disponível para reprodução direta no navegador.

---

## 📁 Estrutura de Arquivos

```
signal-processing-app/
├── app.py                   # Interface web (Streamlit) — camada de apresentação
├── signal_processing.py     # Funções de processamento de sinais — camada lógica
├── requirements.txt         # Dependências do projeto
└── README.md                # Esta documentação
```

---

## 📖 Referência Técnica das Funções

### `signal_processing.py`

#### `normalize_signal(data)`
Normaliza a amplitude do sinal para o intervalo `[-1, 1]`, prevenindo distorções (clipping).

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `data` | `np.ndarray` | Vetor com as amostras do sinal |
| **Retorno** | `np.ndarray` | Sinal normalizado |

---

#### `compute_fft(data, fs)`
Calcula a FFT do sinal e retorna apenas as frequências positivas e suas magnitudes.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `data` | `np.ndarray` | Vetor com as amostras do sinal |
| `fs` | `int` | Frequência de amostragem (Hz) |
| **Retorno** | `tuple(np.ndarray, np.ndarray)` | `(frequências_positivas, magnitudes)` |

---

#### `apply_fir_filter(data, fs, cutoff, filter_type, numtaps=101)`
Projeta e aplica um filtro FIR usando janelamento de Hamming. A filtragem utiliza `scipy.signal.filtfilt` para obter **fase zero** (sem distorção de fase).

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `data` | `np.ndarray` | Vetor do sinal de entrada |
| `fs` | `int` | Frequência de amostragem (Hz) |
| `cutoff` | `float` | Frequência de corte (Hz) |
| `filter_type` | `str` | `"Passa-baixa"` ou `"Passa-alta"` |
| `numtaps` | `int` | Número de coeficientes do filtro (default: 101) |
| **Retorno** | `np.ndarray` | Sinal filtrado |

**Detalhes da implementação:**
1. Normaliza a frequência de corte pela frequência de Nyquist (`fs / 2`).
2. Projeta os coeficientes com `scipy.signal.firwin` e janela de Hamming.
3. Aplica filtragem forward-backward com `filtfilt` para eliminar atraso de fase.

---

#### `calculate_snr(original, filtered)`
Calcula a Relação Sinal-Ruído entre o sinal original e o filtrado.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `original` | `np.ndarray` | Sinal antes da filtragem |
| `filtered` | `np.ndarray` | Sinal após a filtragem |
| **Retorno** | `float` | SNR em decibéis (dB). Retorna `inf` se não houver ruído removido. |

---

### `app.py`

#### `load_and_process_audio(uploaded_file)` — `@st.cache_data`
Lê o arquivo `.wav`, converte estéreo para mono (se necessário) e normaliza. O resultado é armazenado em cache pelo Streamlit para evitar reprocessamento a cada interação do usuário.

#### `process_filter(data, fs, cutoff, filter_type)` — `@st.cache_data`
Wrapper cacheado para a filtragem FIR. Evita recalcular a convolução (operação computacionalmente pesada) quando os parâmetros não mudam.

#### `plot_spectrogram(data, fs)`
Gera o espectrograma (análise tempo-frequência) usando `scipy.signal.spectrogram` e renderiza com `matplotlib` em escala logarítmica (dB).

#### `plot_signal(x, y, title, xlabel, ylabel)`
Função utilitária para renderizar gráficos 2D padronizados com `matplotlib`.

---

## ⚙️ Pipeline de Processamento

O fluxo completo de processamento dos dados segue a seguinte ordem:

```
Upload .wav
    │
    ▼
┌──────────────────────┐
│ 1. Leitura do áudio  │  scipy.io.wavfile.read()
│ 2. Conversão → Mono  │  Se estéreo: média dos canais
│ 3. Normalização      │  data / max(|data|) → [-1, 1]
└──────────┬───────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
┌─────────┐  ┌──────────┐
│  FFT    │  │  STFT    │
│ np.fft  │  │ spectro- │
│         │  │ gram()   │
└────┬────┘  └────┬─────┘
     │            │
     ▼            ▼
  Gráfico     Espectrograma
  Espectral   Tempo-Frequência
           │
           ▼
┌─────────────────────────┐
│ 4. Projeto Filtro FIR   │  firwin() + Hamming
│ 5. Filtragem (filtfilt) │  Fase zero
│ 6. Cálculo SNR          │  10·log10(Ps/Pn) dB
└──────────┬──────────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
  Gráfico      Reprodução
  Filtrado     do Áudio
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Propósito |
|---|---|---|
| [**Python**](https://www.python.org/) | ≥ 3.8 | Linguagem de programação |
| [**Streamlit**](https://streamlit.io/) | Latest | Framework web para dashboards interativos |
| [**NumPy**](https://numpy.org/) | Latest | Computação numérica vetorizada e FFT |
| [**SciPy**](https://scipy.org/) | Latest | Projeto de filtros FIR, leitura de `.wav` e espectrograma |
| [**Matplotlib**](https://matplotlib.org/) | Latest | Visualização de gráficos e espectrogramas |

---

## 📄 Licença

Este projeto é de uso acadêmico/educacional.

---

> **Desenvolvido como ferramenta didática para estudo de Processamento Digital de Sinais e Sistemas LTI.**
