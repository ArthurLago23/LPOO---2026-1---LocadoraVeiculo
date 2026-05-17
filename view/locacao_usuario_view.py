import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox

from control.locacao_controller import LocacaoController
from model.locacao import StatusLocacao


class JanelaLocacaoUsuario(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Locar Veículo - Usuário da Locadora")
        self.geometry("900x480")

        self.controller = LocacaoController()
        self.criar_widgets()
        self.carregar_dados()

    def criar_widgets(self):
        lbl_titulo = tk.Label(
            self,
            text="Locações - Operações do Usuário",
            font=("Helvetica", 16, "bold"),
        )
        lbl_titulo.pack(pady=10)

        frame_tree = tk.Frame(self)
        frame_tree.pack(expand=True, fill="both", padx=20, pady=10)

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("ID", "Placa", "Início", "Fim", "Status")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", yscrollcommand=scrollbar.set)

        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", self._atualizar_botoes)

        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=5)

        self.btn_nova = tk.Button(frame_botoes, text="Nova Reserva", width=12, command=self.abrir_nova_reserva)
        self.btn_nova.pack(side="left", padx=5)

        self.btn_detalhes = tk.Button(frame_botoes, text="Ver Detalhes", width=12, command=self.mostrar_detalhes)
        self.btn_detalhes.pack(side="left", padx=5)

        self.btn_locar = tk.Button(frame_botoes, text="Locar", width=10, command=self.locar)
        self.btn_locar.pack(side="left", padx=5)

        self.btn_devolver = tk.Button(frame_botoes, text="Devolver", width=10, command=self.devolver)
        self.btn_devolver.pack(side="left", padx=5)

        self.btn_cancelar = tk.Button(frame_botoes, text="Cancelar", width=10, command=self.cancelar)
        self.btn_cancelar.pack(side="left", padx=5)

        tk.Button(frame_botoes, text="Fechar", width=10, command=self.destroy).pack(side="right", padx=5)

        self._atualizar_botoes()

    def _obter_id_selecionado(self):
        selecionado = self.tree.selection()
        if not selecionado:
            return None
        return int(self.tree.item(selecionado[0])["values"][0])

    def _obter_status_selecionado(self):
        selecionado = self.tree.selection()
        if not selecionado:
            return None
        return self.tree.item(selecionado[0])["values"][4]

    def _atualizar_botoes(self, event=None):
        status = self._obter_status_selecionado()
        self.btn_locar.config(state="normal" if status == StatusLocacao.RESERVADO.value else "disabled")
        self.btn_devolver.config(state="normal" if status == StatusLocacao.LOCADO.value else "disabled")
        self.btn_cancelar.config(state="normal" if status == StatusLocacao.RESERVADO.value else "disabled")

    def abrir_nova_reserva(self):
        from view.locacao_nova_reserva_view import JanelaNovaReserva
        janela = JanelaNovaReserva(self)
        self.wait_window(janela)
        self.carregar_dados()

    def mostrar_detalhes(self):
        id_locacao = self._obter_id_selecionado()
        if id_locacao is None:
            messagebox.showwarning("Aviso", "Selecione uma locação.", parent=self)
            return

        detalhes = self.controller.obter_detalhes(id_locacao)
        if detalhes:
            messagebox.showinfo("Detalhes da Locação", detalhes, parent=self)
        else:
            messagebox.showerror("Erro", "Locação não encontrada.", parent=self)

    def locar(self):
        id_locacao = self._obter_id_selecionado()
        if id_locacao is None:
            messagebox.showwarning("Aviso", "Selecione uma locação.", parent=self)
            return

        sucesso, msg, _ = self.controller.locar(id_locacao)
        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def devolver(self):
        id_locacao = self._obter_id_selecionado()
        if id_locacao is None:
            messagebox.showwarning("Aviso", "Selecione uma locação.", parent=self)
            return

        sucesso, msg, detalhes = self.controller.devolver(id_locacao)
        if sucesso and detalhes:
            texto = (
                f"Devolução realizada com sucesso!\n\n"
                f"Data de início: {detalhes['data_inicio']}\n"
                f"Data de devolução: {detalhes['data_devolucao']}\n"
                f"Número de diárias: {detalhes['diarias']}\n"
                f"Valor total: R$ {detalhes['valor_total']:.2f}".replace(".", ",")
            )
            messagebox.showinfo("Devolução", texto, parent=self)
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def cancelar(self):
        id_locacao = self._obter_id_selecionado()
        if id_locacao is None:
            messagebox.showwarning("Aviso", "Selecione uma locação.", parent=self)
            return

        if messagebox.askyesno("Confirmar", "Deseja cancelar esta reserva?", parent=self):
            sucesso, msg = self.controller.cancelar(id_locacao)
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", msg, parent=self)

    def carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for loc in self.controller.listar_locacoes():
            fim = loc.data_fim.strftime("%d/%m/%Y") if loc.data_fim else "-"
            self.tree.insert(
                "",
                "end",
                values=(
                    loc.id_locacao,
                    loc.veiculo.placa,
                    loc.data_inicio.strftime("%d/%m/%Y"),
                    fim,
                    loc.status.value,
                ),
            )
        self._atualizar_botoes()
