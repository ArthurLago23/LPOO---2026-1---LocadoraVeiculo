import sys
import os
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox, ttk

from control.locacao_controller import LocacaoController
from model.locacao import StatusLocacao, ESTRATEGIAS


class JanelaCadastroLocacao(tk.Toplevel):
    def __init__(self, master=None, locacao_existente=None):
        super().__init__(master)
        self.locacao_existente = locacao_existente
        self.title("Editar Locação" if locacao_existente else "Nova Locação (Admin)")
        self.geometry("450x420")

        self.controller = LocacaoController()
        self._criar_widgets()

        if locacao_existente:
            self._preencher_dados()

    def _criar_widgets(self):
        texto = "Editar Locação" if self.locacao_existente else "Cadastrar Locação (Admin)"
        tk.Label(self, text=texto, font=("Helvetica", 14, "bold")).pack(pady=10)

        frame_placa = tk.Frame(self)
        frame_placa.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_placa, text="Placa do Veículo:").pack(side="left")
        self.txt_placa = tk.Entry(frame_placa)
        self.txt_placa.pack(side="right", expand=True, fill="x")

        frame_inicio = tk.Frame(self)
        frame_inicio.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_inicio, text="Data Início (DD/MM/AAAA):").pack(side="left")
        self.txt_inicio = tk.Entry(frame_inicio)
        self.txt_inicio.pack(side="right", expand=True, fill="x")

        frame_fim = tk.Frame(self)
        frame_fim.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_fim, text="Data Fim (DD/MM/AAAA):").pack(side="left")
        self.txt_fim = tk.Entry(frame_fim)
        self.txt_fim.pack(side="right", expand=True, fill="x")

        frame_status = tk.Frame(self)
        frame_status.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_status, text="Status:").pack(side="left")
        self.cb_status = ttk.Combobox(
            frame_status,
            values=[s.value for s in StatusLocacao],
            state="readonly",
        )
        self.cb_status.current(0)
        self.cb_status.pack(side="right", expand=True, fill="x")

        frame_estrategia = tk.Frame(self)
        frame_estrategia.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_estrategia, text="Estratégia:").pack(side="left")
        self.cb_estrategia = ttk.Combobox(
            frame_estrategia,
            values=list(ESTRATEGIAS.keys()),
            state="readonly",
        )
        self.cb_estrategia.current(0)
        self.cb_estrategia.pack(side="right", expand=True, fill="x")

        frame_valor = tk.Frame(self)
        frame_valor.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_valor, text="Valor Total (opcional):").pack(side="left")
        self.txt_valor = tk.Entry(frame_valor)
        self.txt_valor.pack(side="right", expand=True, fill="x")

        texto_botao = "Atualizar" if self.locacao_existente else "Salvar"
        tk.Button(self, text=texto_botao, command=self.salvar).pack(pady=20)

        if not self.locacao_existente:
            hoje = date.today().strftime("%d/%m/%Y")
            self.txt_inicio.insert(0, hoje)
            self.txt_fim.insert(0, hoje)

    def _preencher_dados(self):
        loc = self.locacao_existente
        self.txt_placa.insert(0, loc.veiculo.placa)
        self.txt_inicio.insert(0, loc.data_inicio.strftime("%d/%m/%Y"))
        if loc.data_fim:
            self.txt_fim.insert(0, loc.data_fim.strftime("%d/%m/%Y"))
        self.cb_status.set(loc.status.value)
        self.cb_estrategia.set(loc.nome_estrategia)
        if loc.valor_total is not None:
            self.txt_valor.insert(0, f"{loc.valor_total:.2f}")

    def salvar(self):
        id_locacao = self.locacao_existente.id_locacao if self.locacao_existente else None
        sucesso, msg = self.controller.salvar_locacao_admin(
            placa=self.txt_placa.get().strip().upper(),
            data_inicio_str=self.txt_inicio.get().strip(),
            data_fim_str=self.txt_fim.get().strip(),
            status_str=self.cb_status.get(),
            estrategia_nome=self.cb_estrategia.get(),
            valor_total_str=self.txt_valor.get().strip(),
            id_locacao=id_locacao,
        )

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)
