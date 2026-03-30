import os
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


class DNGConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("DNG Converter")
        self.root.geometry("520x380")
        self.root.resizable(False, False)

        self.files = []

        # --- Seleção de origem ---
        frame_src = ttk.LabelFrame(root, text="Origem", padding=10)
        frame_src.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Button(frame_src, text="Selecionar Pasta", command=self.select_folder).pack(side="left", padx=(0, 5))
        ttk.Button(frame_src, text="Selecionar Arquivo(s)", command=self.select_files).pack(side="left")

        self.lbl_src = ttk.Label(frame_src, text="Nenhum selecionado", foreground="gray")
        self.lbl_src.pack(side="left", padx=(10, 0))

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
        self.files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(".dng")
        ]
        self.lbl_src.config(text=f"{len(self.files)} arquivo(s) em {os.path.basename(folder)}", foreground="black")

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

            base = os.path.splitext(filepath)[0]
            ext = ".jpg" if fmt == "jpg" else ".png"
            out_path = base + ext

            try:
                img = self._load_dng(filepath)
                if fmt == "jpg":
                    img.save(out_path, "JPEG", quality=quality)
                else:
                    img.save(out_path, "PNG")
                self.root.after(0, self.log, f"OK: {name} -> {os.path.basename(out_path)}")
                success += 1
            except Exception as e:
                # Fallback: ImageMagick via subprocess
                if HAS_MAGICK:
                    try:
                        cmd = ["magick", filepath]
                        if fmt == "jpg":
                            cmd += ["-quality", str(quality)]
                        cmd.append(out_path)
                        subprocess.run(cmd, check=True, capture_output=True)
                        self.root.after(0, self.log, f"OK (magick): {name} -> {os.path.basename(out_path)}")
                        success += 1
                    except Exception as e2:
                        self.root.after(0, self.log, f"ERRO: {name} - {e2}")
                        errors += 1
                else:
                    self.root.after(0, self.log, f"ERRO: {name} - {e}")
                    errors += 1

            self.root.after(0, self._update_progress, i)

        msg = f"Concluído! {success} convertido(s), {errors} erro(s)."
        self.root.after(0, self.lbl_status.config, {"text": msg})
        self.root.after(0, self.btn_convert.config, {"state": "normal"})

    def _load_dng(self, filepath):
        """Tenta carregar DNG via rawpy, senão via Pillow (TIFF)."""
        # Tentativa 1: rawpy
        if HAS_RAWPY:
            try:
                with rawpy.imread(filepath) as raw:
                    rgb = raw.postprocess()
                return Image.fromarray(rgb)
            except Exception:
                pass

        # Tentativa 2: Pillow (DNG é baseado em TIFF)
        img = Image.open(filepath)
        img.load()
        return img

    def _update_progress(self, value):
        self.progress["value"] = value


if __name__ == "__main__":
    root = tk.Tk()
    app = DNGConverter(root)
    root.mainloop()
