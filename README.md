# DNG to JPG/PNG Converter

Aplicativo desktop simples para converter arquivos **DNG** (Digital Negative) para **JPG** ou **PNG** em lote.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## Funcionalidades

- **Menu de contexto do Windows** — clique direito em qualquer pasta para converter DNGs
- **Busca recursiva** — encontra arquivos DNG em subpastas automaticamente
- **Seleção flexível** — escolha uma pasta inteira ou arquivos individuais (GUI)
- **Formato de saída** — JPG ou PNG, com controle de qualidade para JPG (1–100)
- **Conversão em cascata** — tenta múltiplos métodos para máxima compatibilidade:
  1. `rawpy` (LibRaw) — melhor qualidade para RAW puro
  2. `Pillow` (TIFF) — DNG é baseado em TIFF, funciona com a maioria dos arquivos
  3. `ImageMagick` (subprocess) — fallback final, se instalado no sistema
- **Salva ao lado do original** — mesmo diretório, mesmo nome, só muda a extensão
- **Barra de progresso** — acompanhe a conversão em tempo real com log detalhado
- **Interface não trava** — conversão roda em thread separada

## Instalação

### Pré-requisitos

- Python 3.12 ou superior
- pip

### Passos

```bash
# Clone o repositório
git clone https://github.com/lucasftas/dng-to-jpg-or-png.git
cd dng-to-jpg-or-png

# Instale as dependências
pip install -r requirements.txt
```

### (Opcional) ImageMagick

Para máxima compatibilidade com arquivos DNG exóticos, instale o [ImageMagick](https://imagemagick.org/script/download.php). O app funciona sem ele, mas o usa como fallback quando os outros métodos falham.

## Uso

### Menu de Contexto (recomendado)

Instale o menu de contexto do Windows uma vez:

```bash
python dng_converter.py install
```

Agora basta **clicar com botão direito** em qualquer pasta no Explorer e escolher:
- **Converter DNG → JPG** — converte todos os DNGs da pasta e subpastas para JPG (qualidade 95)
- **Converter DNG → PNG** — converte todos os DNGs da pasta e subpastas para PNG

Para remover o menu de contexto:

```bash
python dng_converter.py uninstall
```

### Interface Gráfica (GUI)

```bash
python dng_converter.py
```

1. Clique em **Selecionar Pasta** ou **Selecionar Arquivo(s)**
2. Marque **Buscar em subpastas** se quiser busca recursiva
3. Escolha o formato: **JPG** ou **PNG**
4. Ajuste a qualidade JPG se necessário (padrão: 95)
5. Clique em **Converter**
6. Acompanhe o progresso na barra e no log

### Linha de Comando (CLI)

```bash
# Converter pasta inteira (recursivo por padrão)
python dng_converter.py convert "C:\Fotos\Viagem" --format jpg --quality 90

# Converter sem buscar em subpastas
python dng_converter.py convert "C:\Fotos" --format png --no-recursive
```

## Estrutura do Projeto

```
dng-to-jpg-or-png/
├── dng_converter.py    # Aplicação principal (GUI + conversão)
├── requirements.txt    # Dependências Python
├── CLAUDE.md           # Instruções para desenvolvimento com IA
├── .gitignore
└── README.md
```

## Dependências

| Pacote   | Função                                      |
|----------|---------------------------------------------|
| `Pillow` | Processamento de imagem, leitura DNG (TIFF) |
| `rawpy`  | Processamento RAW via LibRaw                 |

## Como funciona

O formato DNG (Digital Negative) é um formato RAW aberto baseado em TIFF, criado pela Adobe. O app tenta converter usando múltiplos métodos em cascata:

1. **rawpy/LibRaw** — biblioteca nativa de processamento RAW, melhor qualidade
2. **Pillow** — como DNG é baseado em TIFF, o Pillow consegue ler a maioria dos arquivos DNG diretamente
3. **ImageMagick** — fallback via linha de comando, suporta praticamente qualquer formato

Se um método falha, o próximo é tentado automaticamente. O log mostra qual método foi usado para cada arquivo.

## Licença

MIT
