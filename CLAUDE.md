# DNG to JPG/PNG Converter

## Visão Geral
App desktop Python (tkinter) para conversão em lote de arquivos DNG para JPG ou PNG.

## Stack
- Python 3.12+
- tkinter (GUI nativa)
- Pillow (processamento de imagem, leitura DNG como TIFF)
- rawpy (LibRaw, fallback para RAW processing)
- ImageMagick (fallback via subprocess, opcional)

## Arquitetura
- Arquivo único: `dng_converter.py`
- Conversão em cascata: rawpy → Pillow (TIFF) → ImageMagick subprocess
- Thread separada para conversão (não trava GUI)

## Como rodar
```bash
pip install rawpy Pillow
python dng_converter.py
```

## Convenções
- Commits em português com prefixo convencional (feat:, fix:, docs:, refactor:)
- Manter app simples e arquivo único
