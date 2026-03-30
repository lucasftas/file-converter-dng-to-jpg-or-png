import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image

try:
    import rawpy
    HAS_RAWPY = True
except ImportError:
    HAS_RAWPY = False

HAS_MAGICK = shutil.which("magick") is not None

MENU_ENTRIES = {
    "DNG2JPG": ("Converter DNG \u2192 JPG", "jpg"),
    "DNG2PNG": ("Converter DNG \u2192 PNG", "png"),
}

REGISTRY_ROOTS = [
    r"Software\Classes\Directory\shell",
    r"Software\Classes\Directory\Background\shell",
]


# ---------------------------------------------------------------------------
# Funções standalone de conversão
# ---------------------------------------------------------------------------

def load_dng(filepath):
    """Carrega DNG via rawpy (se disponível), senão via Pillow (TIFF)."""
    if HAS_RAWPY:
        try:
            with rawpy.imread(filepath) as raw:
                rgb = raw.postprocess()
            return Image.fromarray(rgb)
        except Exception:
            pass

    img = Image.open(filepath)
    img.load()
    return img


def convert_file(filepath, fmt="jpg", quality=95):
    """Converte um arquivo DNG. Retorna (out_path, metodo) ou levanta exceção."""
    base = os.path.splitext(filepath)[0]
    ext = ".jpg" if fmt == "jpg" else ".png"
    out_path = base + ext

    try:
        img = load_dng(filepath)
        if fmt == "jpg":
            img.save(out_path, "JPEG", quality=quality)
        else:
            img.save(out_path, "PNG")
        return out_path, "pillow"
    except Exception:
        if HAS_MAGICK:
            cmd = ["magick", filepath]
            if fmt == "jpg":
                cmd += ["-quality", str(quality)]
            cmd.append(out_path)
            subprocess.run(cmd, check=True, capture_output=True)
            return out_path, "magick"
        raise


def find_dng_files(folder, recursive=True):
    """Retorna lista de caminhos .dng na pasta. Recursivo por padrão."""
    p = pathlib.Path(folder)
    pattern = "*.dng"
    gen = p.rglob(pattern) if recursive else p.glob(pattern)
    return sorted(str(f) for f in gen)


# ---------------------------------------------------------------------------
# CLI — conversão, install e uninstall do menu de contexto
# ---------------------------------------------------------------------------

def run_cli_conversion(args):
    folder = args.folder
    fmt = args.format
    quality = args.quality
    recursive = not args.no_recursive

    files = find_dng_files(folder, recursive=recursive)
    if not files:
        print(f"Nenhum arquivo .dng encontrado em: {folder}")
        input("\nPressione Enter para fechar...")
        return

    total = len(files)
    print(f"Encontrados {total} arquivo(s) DNG em: {folder}\n")

    success = 0
    errors = 0
    for i, filepath in enumerate(files, 1):
        name = os.path.basename(filepath)
        try:
            out_path, method = convert_file(filepath, fmt=fmt, quality=quality)
            print(f"  [{i}/{total}] OK ({method}): {name} -> {os.path.basename(out_path)}")
            success += 1
        except Exception as e:
            print(f"  [{i}/{total}] ERRO: {name} - {e}")
            errors += 1

    print(f"\nConcluído! {success} convertido(s), {errors} erro(s).")
    input("\nPressione Enter para fechar...")


def install_context_menu():
    import winreg

    python = sys.executable
    script = os.path.abspath(__file__)

    for root_path in REGISTRY_ROOTS:
        for key_name, (label, fmt) in MENU_ENTRIES.items():
            key_path = f"{root_path}\\{key_name}"
            cmd = f'"{python}" "{script}" convert "%V" --format {fmt}'

            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, label)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{key_path}\\command") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, cmd)

    print("Menu de contexto instalado com sucesso!")
    print("Clique com botão direito em qualquer pasta para ver as opções.")


def uninstall_context_menu():
    import winreg

    for root_path in REGISTRY_ROOTS:
        for key_name in MENU_ENTRIES:
            key_path = f"{root_path}\\{key_name}"
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{key_path}\\command")
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except FileNotFoundError:
                pass

    print("Menu de contexto removido.")


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class DNGConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("DNG Converter")
        self.root.geometry("520x400")
        self.root.resizable(False, False)

        self.files = []

        # --- Seleção de origem ---
        frame_src = ttk.LabelFrame(root, text="Origem", padding=10)
        frame_src.pack(fill="x", padx=10, pady=(10, 5))

        btn_frame = ttk.Frame(frame_src)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="Selecionar Pasta", command=self.select_folder).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Selecionar Arquivo(s)", command=self.select_files).pack(side="left")

        self.lbl_src = ttk.Label(btn_frame, text="Nenhum selecionado", foreground="gray")
        self.lbl_src.pack(side="left", padx=(10, 0))

        self.recursive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame_src, text="Buscar em subpastas", variable=self.recursive_var).pack(anchor="w", pady=(5, 0))

        # --- Formato de saída ---
        frame_fmt = ttk.LabelFrame(root, text="Formato de saída", padding=10)
        frame_fmt.pack(fill="x", padx=10, pady=5)

        self.format_var = tk.StringVar(value="jpg")
        ttk.Radiobutton(frame_fmt, text="JPG", variable=self.format_var, value="jpg").pack(side="left", padx=(0, 15))
        ttk.Radiobutton(frame_fmt, text="PNG", variable=self.format_var, value="png").pack(side="left")

        # --- Qualidade JPG ---
        frame_qual = ttk.Frame(frame_fmt)
        frame_qual.pack(side="left", padx=(30, 0))
        ttk.Label(frame_qual, text="Qualidade JPG:").pack(side="left")
        self.quality_var = tk.IntVar(value=95)
        ttk.Spinbox(frame_qual, from_=1, to=100, width=5, textvariable=self.quality_var).pack(side="left", padx=(5, 0))

        # --- Botão converter ---
        self.btn_convert = ttk.Button(root, text="Converter", command=self.start_conversion)
        self.btn_convert.pack(pady=10)

        # --- Progresso ---
        frame_prog = ttk.LabelFrame(root, text="Progresso", padding=10)
        frame_prog.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.progress = ttk.Progressbar(frame_prog, mode="determinate")
        self.progress.pack(fill="x")

        self.lbl_status = ttk.Label(frame_prog, text="Aguardando...")
        self.lbl_status.pack(anchor="w", pady=(5, 0))

        self.log_text = tk.Text(frame_prog, height=6, state="disabled", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, pady=(5, 0))

    def select_folder(self):
        folder = filedialog.askdirectory(title="Selecione a pasta com arquivos DNG")
        if not folder:
            return
        recursive = self.recursive_var.get()
        self.files = find_dng_files(folder, recursive=recursive)
        label = os.path.basename(folder)
        suffix = " (+ subpastas)" if recursive else ""
        self.lbl_src.config(text=f"{len(self.files)} arquivo(s) em {label}{suffix}", foreground="black")

    def select_files(self):
        paths = filedialog.askopenfilenames(
            title="Selecione arquivos DNG",
            filetypes=[("DNG files", "*.dng"), ("Todos", "*.*")],
        )
        if not paths:
            return
        self.files = list(paths)
        self.lbl_src.config(text=f"{len(self.files)} arquivo(s) selecionado(s)", foreground="black")

    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def start_conversion(self):
        if not self.files:
            messagebox.showwarning("Aviso", "Selecione uma pasta ou arquivo(s) primeiro.")
            return
        self.btn_convert.config(state="disabled")
        self.progress["value"] = 0
        self.progress["maximum"] = len(self.files)
        threading.Thread(target=self.convert_all, daemon=True).start()

    def convert_all(self):
        fmt = self.format_var.get()
        quality = self.quality_var.get()
        total = len(self.files)
        success = 0
        errors = 0

        for i, filepath in enumerate(self.files, 1):
            name = os.path.basename(filepath)
            self.root.after(0, self.lbl_status.config, {"text": f"[{i}/{total}] Convertendo {name}..."})

            try:
                out_path, method = convert_file(filepath, fmt=fmt, quality=quality)
                self.root.after(0, self.log, f"OK ({method}): {name} -> {os.path.basename(out_path)}")
                success += 1
            except Exception as e:
                self.root.after(0, self.log, f"ERRO: {name} - {e}")
                errors += 1

            self.root.after(0, self._update_progress, i)

        msg = f"Concluído! {success} convertido(s), {errors} erro(s)."
        self.root.after(0, self.lbl_status.config, {"text": msg})
        self.root.after(0, self.btn_convert.config, {"state": "normal"})

    def _update_progress(self, value):
        self.progress["value"] = value


def launch_gui():
    root = tk.Tk()
    DNGConverter(root)
    root.mainloop()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def cli_main():
    parser = argparse.ArgumentParser(description="DNG Converter - Converte arquivos DNG para JPG ou PNG")
    sub = parser.add_subparsers(dest="command")

    p_conv = sub.add_parser("convert", help="Converter DNG de uma pasta")
    p_conv.add_argument("folder", help="Pasta com arquivos DNG")
    p_conv.add_argument("--format", choices=["jpg", "png"], default="jpg", help="Formato de saída (padrão: jpg)")
    p_conv.add_argument("--quality", type=int, default=95, help="Qualidade JPG 1-100 (padrão: 95)")
    p_conv.add_argument("--no-recursive", action="store_true", help="Não buscar em subpastas")

    sub.add_parser("install", help="Instalar menu de contexto no Windows")
    sub.add_parser("uninstall", help="Remover menu de contexto do Windows")

    args = parser.parse_args()

    if args.command == "convert":
        run_cli_conversion(args)
    elif args.command == "install":
        install_context_menu()
    elif args.command == "uninstall":
        uninstall_context_menu()
    else:
        launch_gui()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_main()
    else:
        launch_gui()
