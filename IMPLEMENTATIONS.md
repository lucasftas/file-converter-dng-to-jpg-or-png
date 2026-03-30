# Implementations

## v0.1.0 — 2026-03-30

- App desktop para conversão DNG → JPG/PNG com interface tkinter
- Seleção por pasta ou arquivos individuais
- Escolha de formato (JPG/PNG) com controle de qualidade JPG
- Conversão em cascata: rawpy → Pillow (TIFF) → ImageMagick (subprocess)
- Barra de progresso e log em tempo real
- Conversão em thread separada (GUI não trava)
- Arquivo salvo ao lado do original com mesmo nome
