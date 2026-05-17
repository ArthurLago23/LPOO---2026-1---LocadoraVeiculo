import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from view.janela_principal import JanelaPrincipal


if __name__ == "__main__":
    app = JanelaPrincipal()
    app.mainloop()
