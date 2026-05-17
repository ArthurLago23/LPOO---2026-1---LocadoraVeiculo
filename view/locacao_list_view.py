import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.locacao_controller import LocacaoController


class JanelaListagemLocacoes(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Locações - Administrador")
        self.geometry("900x450")

        self.controller = LocacaoController()
        self.criar_widgets()
        self.carregar_dados()

    def criar_widgets(self):
        lbl_titulo = tk.Label(self, text="CRUD de Locações (Admin)", font=("Helvetica", 16, "bold"))
        lbl_titulo.pack(pady=10)

        frame_tree = tk.Frame(self)
        frame_tree.pack(expand=True, fill="both", padx=20, pady=10)

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("ID", "Placa", "Início", "Fim", "Status", "Valor Total")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", yscrollcommand=scrollbar.set)

        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=110)

        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=5)

        tk.Button(frame_botoes, text="Novo", width=10, command=self.abrir_novo).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Editar", width=10, command=self.abrir_editar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Ver Detalhes", width=12, command=self.mostrar_detalhes).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Remover", width=10, command=self.remover_locacao).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Fechar", width=10, command=self.destroy).pack(side="right", padx=5)

    def _obter_id_selecionado(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma locação.", parent=self)
            return None
        item = self.tree.item(selecionado[0])
        return int(item["values"][0])

    def abrir_novo(self):
        from view.locacao_cadastro_view import JanelaCadastroLocacao
        janela = JanelaCadastroLocacao(self)
        self.wait_window(janela)
        self.carregar_dados()

    def abrir_editar(self):
        id_locacao = self._obter_id_selecionado()
        if id_locacao is None:
            return

        locacao = self.controller.buscar_por_id(id_locacao)
        if not locacao:
            messagebox.showerror("Erro", "Locação não encontrada.", parent=self)
            return

        from view.locacao_cadastro_view import JanelaCadastroLocacao
        janela = JanelaCadastroLocacao(self, locacao_existente=locacao)
        self.wait_window(janela)
        self.carregar_dados()

    def mostrar_detalhes(self):
        id_locacao = self._obter_id_selecionado()
        if id_locacao is None:
            return

        detalhes = self.controller.obter_detalhes(id_locacao)
        if detalhes:
            messagebox.showinfo("Detalhes da Locação", detalhes, parent=self)
        else:
            messagebox.showerror("Erro", "Locação não encontrada.", parent=self)

    def remover_locacao(self):
        id_locacao = self._obter_id_selecionado()
        if id_locacao is None:
            return

        if messagebox.askyesno("Confirmar", f"Remover a locação ID {id_locacao}?", parent=self):
            sucesso, msg = self.controller.remover_locacao(id_locacao)
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", msg, parent=self)

    def carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        locacoes = self.controller.listar_locacoes()
        for loc in locacoes:
            fim = loc.data_fim.strftime("%d/%m/%Y") if loc.data_fim else "-"
            valor = (
                f"R$ {loc.valor_total:.2f}".replace(".", ",")
                if loc.valor_total is not None
                else "-"
            )
            self.tree.insert(
                "",
                "end",
                values=(
                    loc.id_locacao,
                    loc.veiculo.placa,
                    loc.data_inicio.strftime("%d/%m/%Y"),
                    fim,
                    loc.status.value,
                    valor,
                ),
            )
