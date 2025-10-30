import customtkinter as ctk
import json
import os
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog, Toplevel, Listbox, MULTIPLE, Scrollbar, END
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

DATA_FILE = "snippets.json"

def cargar_snippets():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_snippets(snippets):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(snippets, f, indent=4, ensure_ascii=False)

class SnippetExportDialog(ctk.CTkToplevel):
    def __init__(self, master, snippets, callback):
        super().__init__(master)
        self.title("Selecciona Snippets para Exportar")
        self.geometry("500x400")
        self.snippets = snippets
        self.selected_indices = []
        self.callback = callback
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        lbl = ctk.CTkLabel(self, text="Selecciona uno o varios snippets para exportar:", font=("Segoe UI", 14))
        lbl.pack(padx=12, pady=10)

        self.listbox_frame = ctk.CTkFrame(self)
        self.listbox_frame.pack(fill="both", expand=True, padx=12, pady=(0,10))

        self.scrollbar = Scrollbar(self.listbox_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.listbox = Listbox(self.listbox_frame, font=("Segoe UI", 12), selectmode=MULTIPLE,
                               yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.listbox.yview)

        for snip in snippets:
            desc = snip.get("descripcion", "Sin Descripción")
            etiquetas = ", ".join(snip.get("etiquetas", []))
            text = f"{desc} [Etiquetas: {etiquetas}]"
            self.listbox.insert(END, text)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ok_btn = ctk.CTkButton(btn_frame, text="Exportar seleccionados", width=180, command=self.export_selected)
        ok_btn.pack(side="left", padx=10)
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancelar", width=100, command=self.on_close)
        cancel_btn.pack(side="left", padx=10)

    def export_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            CTkMessagebox(title="Error", message="Debes seleccionar al menos un snippet.", icon="warning")
            return
        self.selected_indices = selected
        self.callback(self.selected_indices)
        self.destroy()

    def on_close(self):
        self.destroy()


class SnippetManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestor Visual de Snippets")
        self.geometry("1200x700")
        self.after(10, self.maximize_window)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.snippets = cargar_snippets()
        self.editing_index = None

        self.header = ctk.CTkFrame(self, height=80, fg_color=("#1e3c72", "#2a5298"))
        self.header.pack(fill="x")
        ctk.CTkLabel(self.header, text="🔥 Gestor Visual de Snippets", 
                     font=("Segoe UI", 24, "bold"),
                     text_color="#FDE910").pack(pady=20)

        self.theme_selector = ctk.CTkOptionMenu(self.header,
                                                values=["System", "Dark", "Light"],
                                                command=self.cambiar_tema,
                                                width=130, height=40,
                                                font=("Segoe UI", 15))
        self.theme_selector.set("System")
        self.theme_selector.pack(side="right", padx=30, pady=20)

        self.menu_frame = ctk.CTkFrame(self, height=50)
        self.menu_frame.pack(fill="x", padx=10, pady=10)
        self.btn_show_list = ctk.CTkButton(self.menu_frame, text="Lista Snippets", command=self.show_list,
                                           fg_color="#00796b", width=130)
        self.btn_add = ctk.CTkButton(self.menu_frame, text="Nuevo Snippet", command=self.show_add,
                                     fg_color="#4caf50", width=130)
        self.btn_export = ctk.CTkButton(self.menu_frame, text="Exportar PDF", command=self.open_export_dialog,
                                        fg_color="#607d8b", width=130)
        self.btn_clear = ctk.CTkButton(self.menu_frame, text="Limpiar Todo", command=self.limpiar_todo,
                                       fg_color="#d32f2f", width=130)
        self.btn_show_list.pack(side="left", padx=8)
        self.btn_add.pack(side="left", padx=8)
        self.btn_export.pack(side="left", padx=8)
        self.btn_clear.pack(side="left", padx=8)

        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.pack(fill="x", padx=15, pady=5)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Buscar...", textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10,6))
        self.search_var.trace("w", self.filtrar_snippets)
        self.btn_cancel_search = ctk.CTkButton(self.search_frame, text="X", command=self.limpiar_busqueda, width=40)
        self.btn_cancel_search.pack(side="left", padx=(0,10))

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.snippets_list = ctk.CTkScrollableFrame(self.content_frame, corner_radius=15)
        self.snippets_list.pack(fill="both", expand=True)

        self.show_list()

    def maximize_window(self):
        self.state("zoomed")

    def cambiar_tema(self, modo):
        ctk.set_appearance_mode(modo)

    def show_list(self):
        self.clear_content()
        self.populate_snippets()
        self.editing_index = None

    def show_add(self):
        self.clear_content()
        self.editing_index = None
        self.activar_form()

    def activar_form(self, snippet=None):
        self.form_frame = ctk.CTkFrame(self.content_frame)
        self.form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.desc_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Descripción", font=("Segoe UI", 14))
        self.desc_entry.pack(fill="x", pady=8)
        self.tags_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Etiquetas (coma)", font=("Segoe UI", 14))
        self.tags_entry.pack(fill="x", pady=8)
        self.code_entry = ctk.CTkTextbox(self.form_frame, height=180, font=("Consolas", 13))
        self.code_entry.pack(fill="both", pady=8, expand=True)
        btn_text = "Guardar" if snippet is None else "Actualizar"
        self.save_btn = ctk.CTkButton(self.form_frame, text=btn_text, fg_color="#4caf50", font=("Segoe UI", 15, "bold"),
                                     command=self.guardar_snippet)
        self.save_btn.pack(pady=10)

        if snippet:
            self.desc_entry.insert(0, snippet["descripcion"])
            self.tags_entry.insert(0, ", ".join(snippet["etiquetas"]))
            self.code_entry.insert("1.0", snippet["codigo"])
            self.editing_index = self.snippets.index(snippet)

    def guardar_snippet(self):
        desc = self.desc_entry.get().strip()
        tags = [e.strip() for e in self.tags_entry.get().split(",") if e.strip()]
        code = self.code_entry.get("1.0", "end-1c").strip()
        if not desc or not code:
            CTkMessagebox(title="Error", message="Descripción y código obligatorios.", icon="warning")
            return
        if self.editing_index is not None:
            self.snippets[self.editing_index] = {"descripcion": desc, "etiquetas": tags, "codigo": code}
            self.editing_index = None
        else:
            self.snippets.append({"descripcion": desc, "etiquetas": tags, "codigo": code})
        guardar_snippets(self.snippets)
        self.show_list()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def populate_snippets(self):
        self.snippets_list.destroy()
        self.snippets_list = ctk.CTkScrollableFrame(self.content_frame, corner_radius=15)
        self.snippets_list.pack(fill="both", expand=True)
        for i, snip in enumerate(self.snippets):
            frame = ctk.CTkFrame(self.snippets_list, corner_radius=15, fg_color="#e0f7fa" if i % 2 == 0 else "#d0f0fd")
            frame.pack(fill="x", pady=8, padx=16)
            ctk.CTkLabel(frame, text=f"{i+1}. {snip['descripcion']} [Etiquetas: {', '.join(snip['etiquetas'])}]",
                         font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=12, pady=(8,3))
            codebox = ctk.CTkTextbox(frame, height=120, font=("Consolas", 13))
            codebox.pack(fill="x", padx=10, pady=(0,8))
            codebox.insert("1.0", snip["codigo"])
            codebox.configure(state="disabled")
            btn_frame = ctk.CTkFrame(frame)
            btn_frame.pack(fill="x", padx=10, pady=(0,8))
            edit_btn = ctk.CTkButton(btn_frame, text="Editar", width=75, command=lambda s=snip: self.editar_snippet(s))
            edit_btn.pack(side="left")
            del_btn = ctk.CTkButton(btn_frame, text="Eliminar", fg_color="#d32f2f", width=75, command=lambda i=i: self.eliminar_snippet(i))
            del_btn.pack(side="right")

    def filtrar_snippets(self, *args):
        filtro = self.search_var.get().strip().lower()
        if not filtro:
            self.show_list()
            return
        resultados = [s for s in self.snippets if filtro in s["descripcion"].lower() or
                      filtro in " ".join(s["etiquetas"]).lower() or
                      filtro in s["codigo"].lower()]
        self.clear_content()
        self.snippets_list = ctk.CTkScrollableFrame(self.content_frame, corner_radius=15)
        self.snippets_list.pack(fill="both", expand=True)
        for i, snip in enumerate(resultados):
            frame = ctk.CTkFrame(self.snippets_list, corner_radius=15, fg_color="#ffe0b2" if i % 2 == 0 else "#ffd7a7")
            frame.pack(fill="x", pady=8, padx=16)
            ctk.CTkLabel(frame, text=f"{snip['descripcion']} [Etiquetas: {', '.join(snip['etiquetas'])}]",
                         font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=12, pady=(8,3))
            codebox = ctk.CTkTextbox(frame, height=120, font=("Consolas", 13))
            codebox.pack(fill="x", padx=10, pady=(0,8))
            codebox.insert("1.0", snip["codigo"])
            codebox.configure(state="disabled")
            btn_frame = ctk.CTkFrame(frame)
            btn_frame.pack(fill="x", padx=10, pady=(0,8))
            edit_btn = ctk.CTkButton(btn_frame, text="Editar", width=75, command=lambda s=snip: self.editar_snippet(s))
            edit_btn.pack(side="left")
            del_btn = ctk.CTkButton(btn_frame, text="Eliminar", fg_color="#d32f2f", width=75,
                                    command=lambda i=self.snippets.index(snip): self.eliminar_snippet(i))
            del_btn.pack(side="right")

    def limpiar_busqueda(self):
        self.search_var.set("")
        self.show_list()

    def eliminar_snippet(self, idx):
        del self.snippets[idx]
        guardar_snippets(self.snippets)
        self.show_list()

    def editar_snippet(self, snippet):
        self.clear_content()
        self.activar_form(snippet)

    def limpiar_todo(self):
        if CTkMessagebox(title="Confirmar", message="¿Eliminar todos los snippets?", icon="warning"):
            self.snippets = []
            guardar_snippets(self.snippets)
            self.show_list()

    def open_export_dialog(self):
        if not self.snippets:
            CTkMessagebox(title="Info", message="No hay snippets para exportar", icon="info")
            return
        SnippetExportDialog(self, self.snippets, self.export_pdf_with_selection)

    def export_pdf_with_selection(self, selected_indices):
        if not selected_indices:
            CTkMessagebox(title="Error", message="No se seleccionaron snippets para exportar.", icon="warning")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not filepath:
            return
        try:
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            y = height - 40
            c.setFont("Helvetica-Bold", 18)
            c.drawString(40, y, "Snippets Exportados")
            y -= 40
            c.setFont("Helvetica", 12)
            for i, idx in enumerate(selected_indices, 1):
                snip = self.snippets[idx]
                c.drawString(40, y, f"{i}. {snip['descripcion']}")
                y -= 20
                c.setFont("Courier", 10)
                for line in snip["codigo"].splitlines():
                    if y < 40:
                        c.showPage()
                        y = height - 40
                        c.setFont("Helvetica", 12)
                    c.drawString(60, y, line)
                    y -= 14
                c.setFont("Helvetica", 12)
                y -= 15
                if y < 40:
                    c.showPage()
                    y = height - 40
                    c.setFont("Helvetica", 12)
            c.save()
            CTkMessagebox(title="Éxito", message=f"Snippets exportados con éxito a:\n{filepath}", icon="check")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"No se pudo exportar el PDF: {e}", icon="cancel")

if __name__ == "__main__":
    app = SnippetManager()
    app.mainloop()
