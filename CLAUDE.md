# DNG to JPG/PNG Converter

## Visão Geral
App Python (tkinter) para conversão em lote de arquivos DNG para JPG ou PNG.
Suporta GUI, CLI e menu de contexto do Windows.

## Stack
- Python 3.12+
- tkinter (GUI nativa)
- Pillow (processamento de imagem, leitura DNG como TIFF)
- rawpy (LibRaw, fallback para RAW processing)
- ImageMagick (fallback via subprocess, opcional)
- winreg (registro do Windows para menu de contexto)

## Arquitetura
- Arquivo único: `dng_converter.py`
- Funções standalone: `load_dng()`, `convert_file()`, `find_dng_files()`
- Classe GUI: `DNGConverter` (usa funções standalone)
- CLI: argparse com subcomandos `convert`, `install`, `uninstall`
- Conversão em cascata: rawpy → Pillow (TIFF) → ImageMagick subprocess
- Thread separada para conversão na GUI

## Como rodar
```bash
pip install rawpy Pillow
python dng_converter.py              # GUI
python dng_converter.py convert <pasta> --format jpg  # CLI
python dng_converter.py install      # Menu de contexto Windows
python dng_converter.py uninstall    # Remove menu de contexto
```

## Convenções
- Commits em português com prefixo convencional (feat:, fix:, docs:, refactor:)
- Manter app simples e arquivo único

## Instaladores

Sempre que o projeto gerar um instalador funcional (`.exe`, `.msi`, `.dmg`, `.AppImage`, etc.), salvar a última versão funcional na pasta `~Instaladores/` na raiz do projeto. Manter apenas a versão mais recente. Se o projeto não gera instalador, ignorar esta regra.
