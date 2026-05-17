import sys
import os
from datetime import date, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox, ttk

from control.locacao_controller import LocacaoController
from model.locacao import ESTRATEGIAS
from model.veiculo import Categoria


class JanelaNovaReserva(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Nova Reserva")
        self.geometry("480x400")

        self.controller = LocacaoController()
        self._criar_widgets()

    def _criar_widgets(self):
        tk.Label(self, text="Nova Reserva", font=("Helvetica", 14, "bold")).pack(pady=10)

        hoje = date.today()
        fim_padrao = hoje + timedelta(days=3)

        frame_inicio = tk.Frame(self)
        frame_inicio.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_inicio, text="Data Início (DD/MM/AAAA):").pack(side="left")
        self.txt_inicio = tk.Entry(frame_inicio)
        self.txt_inicio.insert(0, hoje.strftime("%d/%m/%Y"))
        self.txt_inicio.pack(side="right", expand=True, fill="x")
        self.txt_inicio.bind("<FocusOut>", lambda e: self._atualizar_veiculos())

        frame_fim = tk.Frame(self)
        frame_fim.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_fim, text="Data Fim (DD/MM/AAAA):").pack(side="left")
        self.txt_fim = tk.Entry(frame_fim)
        self.txt_fim.insert(0, fim_padrao.strftime("%d/%m/%Y"))
        self.txt_fim.pack(side="right", expand=True, fill="x")
        self.txt_fim.bind("<FocusOut>", lambda e: self._atualizar_veiculos())

        frame_cat = tk.Frame(self)
        frame_cat.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_cat, text="Categoria:").pack(side="left")
        self.cb_categoria = ttk.Combobox(
            frame_cat,
            values=[c.name for c in Categoria],
            state="readonly",
        )
        self.cb_categoria.current(0)
        self.cb_categoria.pack(side="right", expand=True, fill="x")
        self.cb_categoria.bind("<<ComboboxSelected>>", lambda e: self._atualizar_veiculos())

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

        frame_veiculo = tk.Frame(self)
        frame_veiculo.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_veiculo, text="Veículo disponível:").pack(side="left")
        self.cb_veiculo = ttk.Combobox(frame_veiculo, state="readonly")
        self.cb_veiculo.pack(side="right", expand=True, fill="x")

        tk.Button(self, text="Atualizar Veículos", command=self._atualizar_veiculos).pack(pady=5)
        tk.Button(self, text="Confirmar Reserva", command=self.confirmar).pack(pady=15)

        self._atualizar_veiculos()

    def _atualizar_veiculos(self):
        sucesso, msg, veiculos = self.controller.buscar_veiculos_disponiveis(
            self.txt_inicio.get().strip(),
            self.txt_fim.get().strip(),
            self.cb_categoria.get(),
        )

        if not sucesso:
            self.cb_veiculo["values"] = []
            self.cb_veiculo.set("")
            messagebox.showwarning("Aviso", msg, parent=self)
            return

        placas = [f"{v.placa} ({type(v).__name__})" for v in veiculos]
        self.cb_veiculo["values"] = placas
        if placas:
            self.cb_veiculo.current(0)
        else:
            self.cb_veiculo.set("")
            messagebox.showinfo("Info", "Nenhum veículo disponível para o período e categoria.", parent=self)

    def confirmar(self):
        if not self.cb_veiculo.get():
            messagebox.showwarning("Aviso", "Selecione um veículo disponível.", parent=self)
            return

        placa = self.cb_veiculo.get().split(" ")[0]
        sucesso, msg = self.controller.criar_reserva(
            placa=placa,
            data_inicio_str=self.txt_inicio.get().strip(),
            data_fim_str=self.txt_fim.get().strip(),
            estrategia_nome=self.cb_estrategia.get(),
            categoria_str=self.cb_categoria.get(),
        )

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)
