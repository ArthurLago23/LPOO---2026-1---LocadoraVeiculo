from datetime import date, datetime
from enum import Enum

from .veiculo import Veiculo
from .ExcecoesPersonalizadas import DataInvalidaError
from .LocacaoStrategy import CalculoLocacaoStrategy, CalculoPadraoStrategy, CalculoVIPStrategy


class StatusLocacao(Enum):
    RESERVADO = "reservado"
    LOCADO = "locado"
    DEVOLVIDO = "devolvido"
    CANCELADO = "cancelado"


ESTRATEGIAS = {
    "CalculoPadraoStrategy": CalculoPadraoStrategy,
    "CalculoVIPStrategy": CalculoVIPStrategy,
}


def criar_estrategia(nome: str) -> CalculoLocacaoStrategy:
    classe = ESTRATEGIAS.get(nome, CalculoPadraoStrategy)
    return classe()


class Locacao:

    def __init__(
        self,
        veiculo: Veiculo,
        data_inicio: date = None,
        data_fim: date = None,
        estrategia: CalculoLocacaoStrategy = None,
        status: StatusLocacao = StatusLocacao.RESERVADO,
        id_locacao: int = None,
        valor_total: float = None,
    ):
        self.__data_inicio = None
        self.__data_fim = None
        self.__id_locacao = id_locacao
        self.__valor_total = valor_total

        self.veiculo = veiculo
        self.data_inicio = data_inicio if data_inicio is not None else datetime.now().date()
        self.data_fim = data_fim
        self.estrategia = estrategia if estrategia is not None else CalculoPadraoStrategy()
        self.status = status

    @property
    def id_locacao(self):
        return self.__id_locacao

    @id_locacao.setter
    def id_locacao(self, valor: int):
        self.__id_locacao = valor

    @property
    def valor_total(self):
        return self.__valor_total

    @valor_total.setter
    def valor_total(self, valor: float):
        self.__valor_total = valor

    @property
    def status(self) -> StatusLocacao:
        return self.__status

    @status.setter
    def status(self, valor):
        if isinstance(valor, str):
            valor = StatusLocacao(valor)
        self.__status = valor

    @property
    def veiculo(self):
        return self.__veiculo

    @veiculo.setter
    def veiculo(self, obj: Veiculo):
        if obj is not None:
            self.__veiculo = obj
        else:
            raise Exception("Objeto Veículo obrigatório!!!")

    @property
    def data_inicio(self):
        return self.__data_inicio

    @data_inicio.setter
    def data_inicio(self, data_inicio: date):
        if self.data_fim is not None and data_inicio > self.data_fim:
            raise DataInvalidaError("Data de início não pode ser posterior à data de fim.")
        elif data_inicio is None:
            raise DataInvalidaError("Data de início é obrigatória!")
        self.__data_inicio = data_inicio

    @property
    def data_fim(self):
        return self.__data_fim

    @data_fim.setter
    def data_fim(self, data_fim: date):
        if data_fim is not None and self.data_inicio > data_fim:
            raise DataInvalidaError("Data de início não pode ser posterior à data de fim.")
        self.__data_fim = data_fim

    @property
    def estrategia(self) -> CalculoLocacaoStrategy:
        return self.__estrategia

    @estrategia.setter
    def estrategia(self, estrategia: CalculoLocacaoStrategy):
        self.__estrategia = estrategia

    @property
    def nome_estrategia(self) -> str:
        return self.estrategia.__class__.__name__

    def calcular_diarias(self) -> int:
        if self.data_fim is None:
            return 1
        dias = (self.data_fim - self.data_inicio).days
        return max(dias, 1)

    def calcular_valor_locacao(self) -> float:
        data_fim_calculo = self.data_fim
        if data_fim_calculo is None:
            data_fim_calculo = date.today()

        dias = (data_fim_calculo - self.data_inicio).days
        if dias <= 0:
            dias = 1

        return float(self.estrategia.calcular_diarias(self.veiculo, dias))
