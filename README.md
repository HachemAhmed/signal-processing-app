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
4. **Projetar** filtros digitais FIR (Passa-baixa ou Passa-alta) com janela de Hamming, escolhendo a frequência de corte e a ordem do filtro.
5. **Inspecionar** a resposta ao impulso `h[n]` e a resposta em frequência `|H(ω)|` do filtro projetado antes de aplicá-lo.
6. **Comparar** o efeito de diferentes ordens de filtro (51 a 251 coeficientes) sobre a nitidez da transição espectral.
7. **Aplicar** a filtragem e comparar o sinal original com o filtrado, tanto no domínio do tempo quanto no da frequência.
8. **Avaliar** a qualidade da filtragem por meio do **Índice de Preservação do Sinal** em dB.
9. **Ouvir** o resultado da filtragem diretamente no navegador e **baixar** o arquivo `.wav` filtrado.

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
- `h[k]` são os coeficientes (taps) do filtro — equivalentes à resposta ao impulso `h[n]` do sistema LTI.
- `M` é a ordem do filtro (número de coeficientes).
- A operação é uma **convolução discreta**.

**Vantagens dos filtros FIR:**
- Sempre estáveis (todos os polos na origem).
- Podem ter fase linear exata (simetria dos coeficientes).
- Projeto mais simples e previsível.

### Janela de Hamming

O projeto do filtro utiliza a **janela de Hamming** para suavizar os coeficientes e reduzir o efeito de ripple (ondulações) na banda de rejeição:

$$w[n] = 0.54 - 0.46 \cdot \cos\left(\frac{2\pi n}{M-1}\right)$$

### Resposta em Frequência H(ω)

A resposta em frequência de um filtro FIR é obtida pela DTFT da resposta ao impulso `h[n]`:

$$H(\omega) = \sum_{n=0}^{M-1} h[n] \cdot e^{-j\omega n}$$

A aplicação exibe `|H(ω)|` em dB com marcadores de referência na frequência de corte projetada e no ponto de -3 dB (frequência de corte real), permitindo verificar visualmente a qualidade do projeto do filtro.

### Espectrograma (STFT)

O espectrograma é obtido pela **Short-Time Fourier Transform (STFT)**, que aplica a FFT em janelas deslizantes ao longo do sinal, revelando como as frequências variam ao longo do tempo.

### Índice de Preservação do Sinal

A métrica calculada pela aplicação quantifica o quanto a filtragem preservou o conteúdo espectral do sinal, medida em decibéis (dB):

$$\text{IPS}_{dB} = 10 \cdot \log_{10}\left(\frac{P_{\text{filtrado}}}{P_{\text{removido}}}\right)$$

Onde:
- `P_filtrado` = potência média do sinal após a filtragem.
- `P_removido` = potência média da diferença entre o sinal original e o filtrado.

> **Nota:** Esta métrica não representa o SNR tradicional (sinal vs. ruído de fundo captado). Ela mede o quanto o filtro alterou o sinal original. Valores altos indicam que a filtragem preservou a maior parte da energia; valores baixos são esperados quando o filtro remove uma faixa espectral significativa (ex.: passa-alta com frequência de corte alta).

---

## 🏗️ Arquitetura do Sistema

A aplicação segue uma arquitetura em **duas camadas** com separação clara de responsabilidades:

```
┌──────────────────────────────────────────────────────────────┐
│                     app.py (Camada UI)                       │
│  ┌─────────────┐  ┌─────────────────────┐  ┌─────────────┐  │
│  │ Upload .wav  │  │ Controles Interativos│  │Visualização │  │
│  │             │  │ Tipo | Corte | Ordem │  │ Matplotlib  │  │
│  └──────┬──────┘  └──────────┬──────────┘  └──────▲──────┘  │
│         │                    │                     │         │
│         │     ┌──────────────▼──────────────┐      │         │
│         │     │  Cache (st.cache_data)       │      │         │
│         │     │  load_and_process_audio      │      │         │
│         │     │  get_filter_design           │      │         │
│         │     │  process_filter              │      │         │
│         │     └──────────────┬──────────────┘      │         │
└─────────┼────────────────────┼─────────────────────┼─────────┘
          │                    │                     │
          ▼                    ▼                     │
┌──────────────────────────────────────────────────────────────┐
│            signal_processing.py (Camada Lógica)              │
│  ┌──────────────────┐        ┌──────────────────────────┐    │
│  │ normalize_signal │        │     design_fir_filter    │    │
│  │ compute_fft      │        │     apply_fir_filter     ├────┘
│  │                  │        │ compute_frequency_response│
│  └──────────────────┘        │     calculate_snr        │
│                              └──────────────────────────┘
│                         NumPy + SciPy                        │
└──────────────────────────────────────────────────────────────┘
```

| Camada | Arquivo | Responsabilidade |
|---|---|---|
| **Interface (UI)** | `app.py` | Upload de arquivos, controles interativos, renderização de gráficos, reprodução e download de áudio |
| **Lógica Matemática** | `signal_processing.py` | Normalização, FFT, projeto e aplicação de filtros FIR, resposta em frequência e cálculo do índice de preservação |

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
- **Reprodução de áudio:** Player direto no navegador.
- **Gráfico Temporal:** Amplitude × Tempo do sinal completo.
- **Gráfico Espectral (FFT):** Magnitude × Frequência, mostrando as componentes de frequência presentes.
- **Espectrograma (STFT):** Mapa de calor mostrando a evolução das frequências ao longo do tempo.

### Passo 3 — Projetar o filtro
Configure os parâmetros do filtro FIR na Seção 2:
- **Tipo:** `Passa-baixa` (atenua frequências acima do corte) ou `Passa-alta` (atenua frequências abaixo do corte).
- **Frequência de Corte:** Ajuste com o slider (100 Hz até `fs/2 - 100` Hz).
- **Ordem do Filtro:** Selecione o número de coeficientes (51, 101, 151, 201 ou 251). Ordens maiores produzem uma transição espectral mais abrupta ao custo de maior processamento.

Ao alterar qualquer parâmetro, a aplicação atualiza automaticamente:
- **`|H(ω)|` em dB:** Resposta em frequência do filtro projetado, com marcadores em -3 dB e na frequência de corte configurada.
- **`h[n]`:** Resposta ao impulso discreta — os próprios coeficientes do filtro FIR.

### Passo 4 — Avaliar o resultado
A Seção 3 exibe:
- O **Índice de Preservação do Sinal** em dB (quanto do sinal foi mantido após a filtragem).
- Gráficos do sinal filtrado no domínio do tempo e da frequência.
- O **áudio filtrado** para reprodução direta no navegador.
- Botão **"⬇️ Baixar Áudio Filtrado (.wav)"** para salvar o resultado localmente.

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
Converte o array para `float64` e normaliza a amplitude para o intervalo `[-1, 1]`, prevenindo distorções (clipping) e garantindo compatibilidade com sinais de entrada inteiros (`int16`, `int32`) ou de ponto flutuante.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `data` | `np.ndarray` | Vetor com as amostras do sinal (qualquer dtype numérico) |
| **Retorno** | `np.ndarray (float64)` | Sinal normalizado no intervalo `[-1, 1]` |

---

#### `compute_fft(data, fs)`
Calcula a FFT do sinal e retorna apenas as frequências positivas e suas magnitudes.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `data` | `np.ndarray` | Vetor com as amostras do sinal |
| `fs` | `int` | Frequência de amostragem (Hz) |
| **Retorno** | `tuple(np.ndarray, np.ndarray)` | `(frequências_positivas, magnitudes)` |

---

#### `design_fir_filter(fs, cutoff, filter_type, numtaps=101)`
Projeta o filtro FIR com janela de Hamming e retorna os coeficientes `h[n]`. Separado de `apply_fir_filter` para permitir cache e visualização independentes da filtragem.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `fs` | `int` | Frequência de amostragem (Hz) |
| `cutoff` | `float` | Frequência de corte (Hz) |
| `filter_type` | `str` | `"Passa-baixa"` ou `"Passa-alta"` |
| `numtaps` | `int` | Número de coeficientes do filtro (default: 101) |
| **Retorno** | `np.ndarray` | Vetor de coeficientes `h[n]` do filtro FIR |

---

#### `apply_fir_filter(data, fs, cutoff, filter_type, numtaps=101)`
Aplica o filtro FIR ao sinal usando `scipy.signal.filtfilt` para **filtragem de fase zero** (passa o sinal nos dois sentidos, eliminando distorção de fase). Internamente chama `design_fir_filter` para manter o projeto centralizado.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `data` | `np.ndarray` | Vetor do sinal de entrada |
| `fs` | `int` | Frequência de amostragem (Hz) |
| `cutoff` | `float` | Frequência de corte (Hz) |
| `filter_type` | `str` | `"Passa-baixa"` ou `"Passa-alta"` |
| `numtaps` | `int` | Número de coeficientes do filtro (default: 101) |
| **Retorno** | `np.ndarray` | Sinal filtrado com fase zero |

---

#### `compute_frequency_response(taps, fs)`
Calcula a resposta em frequência `H(ω)` do filtro FIR em dB, usando 8192 pontos para alta resolução espectral.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `taps` | `np.ndarray` | Coeficientes `h[n]` do filtro FIR |
| `fs` | `int` | Frequência de amostragem (Hz) |
| **Retorno** | `tuple(np.ndarray, np.ndarray)` | `(frequências em Hz, magnitude em dB)` |

---

#### `calculate_snr(original, filtered)`
Calcula o Índice de Preservação do Sinal entre o sinal original e o filtrado.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `original` | `np.ndarray` | Sinal antes da filtragem |
| `filtered` | `np.ndarray` | Sinal após a filtragem |
| **Retorno** | `float` | Índice em dB. Retorna `inf` se o filtro não alterou o sinal. |

---

### `app.py`

#### `load_and_process_audio(uploaded_file)` — `@st.cache_data`
Lê o arquivo `.wav`, converte estéreo para mono (se necessário) e normaliza para `float64`. O resultado é armazenado em cache pelo Streamlit para evitar reprocessamento a cada interação.

#### `get_filter_design(fs, cutoff, filter_type, numtaps)` — `@st.cache_data`
Wrapper cacheado para `design_fir_filter`. Permite que a resposta ao impulso e a resposta em frequência sejam renderizadas sem recalcular os coeficientes a cada rerun do Streamlit.

#### `process_filter(data, fs, cutoff, filter_type, numtaps)` — `@st.cache_data`
Wrapper cacheado para a filtragem FIR. Evita recalcular a convolução (operação computacionalmente pesada) quando os parâmetros não mudam.

#### `plot_spectrogram(data, fs)`
Gera o espectrograma (análise tempo-frequência) usando `scipy.signal.spectrogram` e renderiza com `matplotlib` em escala logarítmica (dB).

#### `plot_signal(x, y, title, xlabel, ylabel)`
Função utilitária para renderizar gráficos 2D padronizados com `matplotlib`.

#### `plot_frequency_response(taps, fs, cutoff)`
Plota `|H(ω)|` em dB com dois marcadores de referência: linha horizontal em -3 dB (ponto de corte real) e linha vertical na frequência de corte projetada.

#### `plot_impulse_response(taps)`
Plota a resposta ao impulso discreta `h[n]` usando `stem`. Para filtros FIR, os coeficientes retornados por `firwin` são exatamente `h[n]`.

---

## ⚙️ Pipeline de Processamento

O fluxo completo de processamento dos dados segue a seguinte ordem:

```
Upload .wav
    │
    ▼
┌───────────────────────────┐
│ 1. Leitura do áudio       │  scipy.io.wavfile.read()
│ 2. Conversão → Mono       │  Se estéreo: média dos canais
│ 3. Cast → float64         │  data.astype(np.float64)
│ 4. Normalização           │  data / max(|data|) → [-1, 1]
└─────────────┬─────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌─────────┐      ┌──────────┐
│   FFT   │      │   STFT   │
│ np.fft  │      │ spectro- │
│         │      │ gram()   │
└────┬────┘      └────┬─────┘
     │                │
     ▼                ▼
 Espectro        Espectrograma
 (FFT)           Tempo-Frequência
              │
              ▼
┌─────────────────────────────────┐
│ 5. Projeto do Filtro FIR        │  firwin() + Hamming → h[n]
│    design_fir_filter()          │
├─────────────────────────────────┤
│          ┌──────────┐           │
│          ▼          ▼           │
│  compute_frequency  h[n]        │
│  _response() → H(ω)             │
│  Gráfico |H(ω)| dB  Gráfico h[n]│
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ 6. Filtragem (filtfilt)         │  Fase zero — sem distorção
│ 7. np.clip(filtered, -1, 1)     │  Proteção contra clipping
│ 8. Cálculo IPS                  │  10·log10(Ps/Pn) dB
└──────────────┬──────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
  Gráfico           Reprodução
  Filtrado          + Download .wav
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Propósito |
|---|---|---|
| [**Python**](https://www.python.org/) | ≥ 3.8 | Linguagem de programação |
| [**Streamlit**](https://streamlit.io/) | Latest | Framework web para dashboards interativos |
| [**NumPy**](https://numpy.org/) | Latest | Computação numérica vetorizada e FFT |
| [**SciPy**](https://scipy.org/) | Latest | Projeto de filtros FIR (`firwin`, `filtfilt`, `freqz`), leitura de `.wav` e espectrograma |
| [**Matplotlib**](https://matplotlib.org/) | Latest | Visualização de gráficos, espectrogramas e resposta ao impulso |

---

## 📄 Licença

Este projeto é de uso acadêmico/educacional.

---

> **Desenvolvido como ferramenta didática para estudo de Processamento Digital de Sinais e Sistemas LTI.**