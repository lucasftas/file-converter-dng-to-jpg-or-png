# DNG to JPG/PNG Converter

> Converta arquivos **DNG** para **JPG** ou **PNG** com um clique — via interface gráfica, menu de contexto do Windows ou linha de comando.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## Por que usar?

Câmeras profissionais e smartphones salvam fotos em **DNG** (Digital Negative), um formato RAW da Adobe. Esse formato preserva a qualidade máxima, mas não abre em qualquer lugar. Este app converte seus DNGs para JPG ou PNG de forma rápida e em lote.

---

## Início Rápido

```bash
git clone https://github.com/lucasftas/dng-to-jpg-or-png.git
cd dng-to-jpg-or-png
pip install -r requirements.txt
python dng_converter.py
```

Pronto — a interface gráfica vai abrir. Selecione a pasta com seus DNGs e clique em **Converter**.

---

## 3 Formas de Usar

### 1. Interface Gráfica (GUI)

```bash
python dng_converter.py
```

1. Clique em **Selecionar Pasta** ou **Selecionar Arquivo(s)**
2. Escolha o formato: **JPG** ou **PNG**
3. Ajuste a qualidade (para JPG, padrão: 95)
4. Clique em **Converter** e acompanhe o progresso

### 2. Menu de Contexto do Windows (recomendado)

Instale uma vez:

```bash
python dng_converter.py install
```

Depois, basta **clicar com botão direito** em qualquer pasta no Explorer:

- **Converter DNG → JPG** — converte tudo (incluindo subpastas)
- **Converter DNG → PNG** — idem, em PNG

Para remover: `python dng_converter.py uninstall`

### 3. Linha de Comando (CLI)

```bash
# Pasta inteira (busca em subpastas por padrão)
python dng_converter.py convert "C:\Fotos\Viagem" --format jpg --quality 90

# Sem buscar em subpastas
python dng_converter.py convert "C:\Fotos" --format png --no-recursive
```

---

## Funcionalidades

| Recurso | Descrição |
|---------|-----------|
| Conversão em lote | Converte centenas de arquivos de uma vez |
| Busca recursiva | Encontra DNGs em subpastas automaticamente |
| 3 métodos de conversão | `rawpy` → `Pillow` → `ImageMagick` (tenta o próximo se um falhar) |
| Qualidade ajustável | Controle de 1–100 para JPG |
| Interface responsiva | Barra de progresso em tempo real, sem travar |
| Salva ao lado do original | Mesmo diretório, mesmo nome, só muda a extensão |

---

## Requisitos

- **Python 3.12+**
- **Pillow** e **rawpy** (instalados via `pip install -r requirements.txt`)
- **ImageMagick** *(opcional)* — [baixe aqui](https://imagemagick.org/script/download.php) para compatibilidade com DNGs mais exóticos

---

## Como funciona por dentro

O DNG é um formato RAW baseado em TIFF. O app tenta converter usando 3 métodos em cascata:

1. **rawpy/LibRaw** — melhor qualidade, ideal para RAW puro
2. **Pillow** — lê DNG como TIFF, funciona com a maioria dos arquivos
3. **ImageMagick** — fallback via linha de comando, suporta praticamente tudo

Se um método falha, o próximo é tentado automaticamente. O log mostra qual método foi usado para cada arquivo.

---

## Licença

MIT
