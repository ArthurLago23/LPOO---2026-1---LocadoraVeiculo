from datetime import date, datetime

from dao.locacao_dao import LocacaoDAO
from model.locacao import Locacao, StatusLocacao, criar_estrategia, ESTRATEGIAS
from model.veiculo import Categoria
from model.ExcecoesPersonalizadas import DataInvalidaError
from dao.veiculo_dao import VeiculoDAO


class LocacaoController:
    def __init__(self):
        self.locacao_dao = LocacaoDAO()
        self.veiculo_dao = VeiculoDAO()

    @staticmethod
    def parse_data(data_str: str) -> date:
        data_str = data_str.strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(data_str, fmt).date()
            except ValueError:
                continue
        raise ValueError("Data inválida. Use o formato DD/MM/AAAA")

    def listar_locacoes(self):
        try:
            return self.locacao_dao.listar_todos()
        except Exception as e:
            print(f"Erro ao listar locações: {e}")
            return []

    def buscar_por_id(self, id_locacao: int):
        return self.locacao_dao.buscar_por_id(id_locacao)

    def buscar_veiculos_disponiveis(self, data_inicio_str: str, data_fim_str: str, categoria_str: str, id_locacao_ignorar: int = None):
        try:
            data_inicio = self.parse_data(data_inicio_str)
            data_fim = self.parse_data(data_fim_str)
            if data_inicio > data_fim:
                return False, "Data de início deve ser anterior ou igual à data de fim.", []

            categoria = Categoria[categoria_str.upper()]
            veiculos = self.locacao_dao.buscar_veiculos_disponiveis(
                data_inicio, data_fim, categoria, id_locacao_ignorar
            )
            return True, "", veiculos
        except KeyError:
            return False, "Categoria inválida. Use ECONOMICO ou EXECUTIVO", []
        except ValueError as e:
            return False, str(e), []
        except Exception as e:
            return False, f"Erro inesperado: {e}", []

    def criar_reserva(self, placa: str, data_inicio_str: str, data_fim_str: str, estrategia_nome: str, categoria_str: str):
        try:
            data_inicio = self.parse_data(data_inicio_str)
            data_fim = self.parse_data(data_fim_str)
            if data_inicio > data_fim:
                return False, "Data de início deve ser anterior ou igual à data de fim."

            categoria = Categoria[categoria_str.upper()]
            disponiveis = self.locacao_dao.buscar_veiculos_disponiveis(data_inicio, data_fim, categoria)
            placas = [v.placa for v in disponiveis]
            if placa not in placas:
                return False, "Veículo indisponível para o período e categoria informados."

            veiculo = self.veiculo_dao.buscar_por_placa(placa)
            if not veiculo:
                return False, f"Veículo com placa {placa} não encontrado."

            locacao = Locacao(
                veiculo=veiculo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                estrategia=criar_estrategia(estrategia_nome),
                status=StatusLocacao.RESERVADO,
            )
            return self.locacao_dao.salvar(locacao)
        except DataInvalidaError as e:
            return False, str(e)
        except KeyError:
            return False, "Categoria inválida."
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def salvar_locacao_admin(
        self,
        placa: str,
        data_inicio_str: str,
        data_fim_str: str,
        status_str: str,
        estrategia_nome: str,
        valor_total_str: str = "",
        id_locacao: int = None,
    ):
        try:
            data_inicio = self.parse_data(data_inicio_str)
            data_fim = self.parse_data(data_fim_str) if data_fim_str.strip() else None
            if data_fim and data_inicio > data_fim:
                return False, "Data de início deve ser anterior ou igual à data de fim."

            veiculo = self.veiculo_dao.buscar_por_placa(placa)
            if not veiculo:
                return False, f"Veículo com placa {placa} não encontrado."

            status = StatusLocacao(status_str.lower())
            if estrategia_nome not in ESTRATEGIAS:
                return False, "Estratégia de cálculo inválida."

            valor_total = None
            if valor_total_str.strip():
                valor_total = float(valor_total_str.replace(",", "."))

            locacao = Locacao(
                veiculo=veiculo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                estrategia=criar_estrategia(estrategia_nome),
                status=status,
                id_locacao=id_locacao,
                valor_total=valor_total,
            )

            if id_locacao:
                return self.locacao_dao.atualizar(locacao)
            return self.locacao_dao.salvar(locacao)
        except DataInvalidaError as e:
            return False, str(e)
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def remover_locacao(self, id_locacao: int):
        if not id_locacao:
            return False, "ID da locação não informado"
        return self.locacao_dao.remover(id_locacao)

    def locar(self, id_locacao: int):
        locacao = self.locacao_dao.buscar_por_id(id_locacao)
        if not locacao:
            return False, "Locação não encontrada.", None

        if locacao.status != StatusLocacao.RESERVADO:
            return False, "Somente locações com status 'reservado' podem ser locadas.", None

        hoje = date.today()
        if locacao.data_inicio != hoje:
            locacao.data_inicio = hoje

        locacao.status = StatusLocacao.LOCADO
        sucesso, msg = self.locacao_dao.atualizar(locacao)
        return sucesso, msg, locacao

    def devolver(self, id_locacao: int):
        locacao = self.locacao_dao.buscar_por_id(id_locacao)
        if not locacao:
            return False, "Locação não encontrada.", None

        if locacao.status != StatusLocacao.LOCADO:
            return False, "Somente locações com status 'locado' podem ser devolvidas.", None

        hoje = date.today()
        if locacao.data_inicio >= hoje:
            return False, "Data de início deve ser anterior à data atual para devolução.", None

        locacao.data_fim = hoje
        locacao.valor_total = locacao.calcular_valor_locacao()
        locacao.status = StatusLocacao.DEVOLVIDO
        sucesso, msg = self.locacao_dao.atualizar(locacao)

        detalhes = {
            "data_inicio": locacao.data_inicio.strftime("%d/%m/%Y"),
            "data_devolucao": hoje.strftime("%d/%m/%Y"),
            "diarias": locacao.calcular_diarias(),
            "valor_total": locacao.valor_total,
        }
        return sucesso, msg, detalhes

    def cancelar(self, id_locacao: int):
        locacao = self.locacao_dao.buscar_por_id(id_locacao)
        if not locacao:
            return False, "Locação não encontrada."

        if locacao.status != StatusLocacao.RESERVADO:
            return False, "Somente locações com status 'reservado' podem ser canceladas."

        locacao.status = StatusLocacao.CANCELADO
        return self.locacao_dao.atualizar(locacao)

    def obter_detalhes(self, id_locacao: int):
        locacao = self.locacao_dao.buscar_por_id(id_locacao)
        if not locacao:
            return None

        placa = locacao.veiculo.placa
        status = locacao.status.value
        linhas = [
            f"ID: {locacao.id_locacao}",
            f"Veículo: {placa}",
            f"Status: {status}",
            f"Estratégia: {locacao.nome_estrategia}",
        ]

        if locacao.status == StatusLocacao.DEVOLVIDO:
            linhas.extend([
                f"Data de início: {locacao.data_inicio.strftime('%d/%m/%Y')}",
                f"Data de devolução: {locacao.data_fim.strftime('%d/%m/%Y')}",
                f"Número de diárias: {locacao.calcular_diarias()}",
                f"Valor total: R$ {locacao.valor_total:.2f}".replace(".", ","),
            ])
        elif locacao.status == StatusLocacao.CANCELADO:
            linhas.extend([
                f"Data de início: {locacao.data_inicio.strftime('%d/%m/%Y')}",
                f"Data de fim prevista: {locacao.data_fim.strftime('%d/%m/%Y') if locacao.data_fim else '-'}",
                "Esta locação foi cancelada.",
            ])
        else:
            valor_estimado = locacao.calcular_valor_locacao()
            linhas.extend([
                f"Data de início: {locacao.data_inicio.strftime('%d/%m/%Y')}",
                f"Data de fim prevista: {locacao.data_fim.strftime('%d/%m/%Y') if locacao.data_fim else '-'}",
                f"Valor estimado: R$ {valor_estimado:.2f}".replace(".", ","),
            ])

        return "\n".join(linhas)
