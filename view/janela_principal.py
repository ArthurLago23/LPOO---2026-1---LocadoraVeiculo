import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk


class JanelaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Locadora de Veículos - LPOO")
        self.geometry("500x300")

        lbl = tk.Label(
            self,
            text="Sistema de Locadora de Veículos",
            font=("Helvetica", 18, "bold"),
        )
        lbl.pack(pady=40)

        lbl_info = tk.Label(
            self,
            text="Utilize o menu superior para acessar as funcionalidades.",
            font=("Helvetica", 11),
        )
        lbl_info.pack(pady=10)

        self._criar_menu()

    def _criar_menu(self):
        menubar = tk.Menu(self)

        menu_cadastro = tk.Menu(menubar, tearoff=0)
        menu_cadastro.add_command(label="Veículo", command=self._abrir_veiculos)
        menu_cadastro.add_command(label="Locações (Admin)", command=self._abrir_locacoes_admin)
        menubar.add_cascade(label="Cadastro", menu=menu_cadastro)

        menu_acao = tk.Menu(menubar, tearoff=0)
        menu_acao.add_command(label="Locar Veículo", command=self._abrir_locacao_usuario)
        menubar.add_cascade(label="Ação", menu=menu_acao)

        self.config(menu=menubar)

    def _abrir_veiculos(self):
        from view.veiculo_list_view import JanelaListagemVeiculos
        JanelaListagemVeiculos(self)

    def _abrir_locacoes_admin(self):
        from view.locacao_list_view import JanelaListagemLocacoes
        JanelaListagemLocacoes(self)

    def _abrir_locacao_usuario(self):
        from view.locacao_usuario_view import JanelaLocacaoUsuario
        JanelaLocacaoUsuario(self)
