import sys
import os
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.locacao import Locacao, StatusLocacao, criar_estrategia
from model.veiculo import VeiculoFactory, Categoria
from dao.db_config import DatabaseConfig
from dao.generic_dao import GenericDAO
from dao.veiculo_dao import VeiculoDAO


class LocacaoDAO(GenericDAO):
    STATUS_ATIVOS = ('reservado', 'locado')

    def __init__(self):
        self.conexao = DatabaseConfig.get_connection()
        self.veiculo_dao = VeiculoDAO()

    def _mapear_linha(self, linha) -> Locacao:
        veiculo = self.veiculo_dao.buscar_por_placa(linha[1])
        if veiculo is None:
            raise Exception(f"Veículo {linha[1]} não encontrado para a locação {linha[0]}")

        locacao = Locacao(
            veiculo=veiculo,
            data_inicio=linha[2],
            data_fim=linha[3],
            estrategia=criar_estrategia(linha[5]),
            status=StatusLocacao(linha[4]),
            id_locacao=linha[0],
            valor_total=float(linha[6]) if linha[6] is not None else None,
        )
        return locacao

    def salvar(self, objeto: Locacao):
        if not self.conexao:
            return False, "Sem conexão com o BD"

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """
                INSERT INTO tb_locacoes
                (vei_placa, loc_data_inicio, loc_data_fim, loc_status, loc_estrategia, loc_valor_total)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING loc_id
            """
            cursor.execute(
                query,
                (
                    objeto.veiculo.placa,
                    objeto.data_inicio,
                    objeto.data_fim,
                    objeto.status.value,
                    objeto.nome_estrategia,
                    objeto.valor_total,
                ),
            )
            objeto.id_locacao = cursor.fetchone()[0]
            self.conexao.commit()
            return True, "Locação cadastrada com sucesso"
        except Exception as e:
            print(f"Erro ao inserir locação: {e}")
            self.conexao.rollback()
            return False, f"Erro ao inserir locação: {e}"
        finally:
            if cursor:
                cursor.close()

    def listar_todos(self):
        if not self.conexao:
            return []

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """
                SELECT loc_id, vei_placa, loc_data_inicio, loc_data_fim,
                       loc_status, loc_estrategia, loc_valor_total
                FROM tb_locacoes
                ORDER BY loc_id DESC
            """
            cursor.execute(query)
            return [self._mapear_linha(linha) for linha in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao listar locações: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def buscar_por_id(self, id_locacao: int):
        if not self.conexao:
            return None

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """
                SELECT loc_id, vei_placa, loc_data_inicio, loc_data_fim,
                       loc_status, loc_estrategia, loc_valor_total
                FROM tb_locacoes
                WHERE loc_id = %s
            """
            cursor.execute(query, (id_locacao,))
            linha = cursor.fetchone()
            if linha:
                return self._mapear_linha(linha)
            return None
        except Exception as e:
            print(f"Erro ao buscar locação {id_locacao}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def atualizar(self, objeto: Locacao):
        if not self.conexao:
            return False, "Sem conexão com o BD"
        if objeto.id_locacao is None:
            return False, "ID da locação é obrigatório para atualização"

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """
                UPDATE tb_locacoes
                SET vei_placa = %s, loc_data_inicio = %s, loc_data_fim = %s,
                    loc_status = %s, loc_estrategia = %s, loc_valor_total = %s
                WHERE loc_id = %s
            """
            cursor.execute(
                query,
                (
                    objeto.veiculo.placa,
                    objeto.data_inicio,
                    objeto.data_fim,
                    objeto.status.value,
                    objeto.nome_estrategia,
                    objeto.valor_total,
                    objeto.id_locacao,
                ),
            )
            self.conexao.commit()
            return True, "Locação atualizada com sucesso"
        except Exception as e:
            print(f"Erro ao atualizar locação: {e}")
            self.conexao.rollback()
            return False, f"Erro ao atualizar locação: {e}"
        finally:
            if cursor:
                cursor.close()

    def remover(self, id_objeto: int):
        if not self.conexao:
            return False, "Sem conexão com o BD"

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = "DELETE FROM tb_locacoes WHERE loc_id = %s"
            cursor.execute(query, (id_objeto,))
            self.conexao.commit()
            return True, "Locação removida com sucesso"
        except Exception as e:
            print(f"Erro ao remover locação {id_objeto}: {e}")
            self.conexao.rollback()
            return False, f"Erro ao remover locação: {e}"
        finally:
            if cursor:
                cursor.close()

    def _periodos_conflitam(self, inicio_novo: date, fim_novo: date, inicio_existente: date, fim_existente: date) -> bool:
        fim_novo_efetivo = fim_novo if fim_novo is not None else date.max
        fim_existente_efetivo = fim_existente if fim_existente is not None else date.max
        return inicio_novo <= fim_existente_efetivo and inicio_existente <= fim_novo_efetivo

    def buscar_veiculos_disponiveis(self, data_inicio: date, data_fim: date, categoria: Categoria, id_locacao_ignorar: int = None):
        if not self.conexao:
            return []

        veiculos = self.veiculo_dao.listar_todos()
        veiculos_categoria = [
            v for v in veiculos
            if (v.categoria == categoria if isinstance(v.categoria, Categoria) else str(v.categoria) == categoria.value)
        ]

        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """
                SELECT loc_id, vei_placa, loc_data_inicio, loc_data_fim, loc_status
                FROM tb_locacoes
                WHERE loc_status IN ('reservado', 'locado')
            """
            if id_locacao_ignorar:
                query += " AND loc_id <> %s"
                cursor.execute(query, (id_locacao_ignorar,))
            else:
                cursor.execute(query)

            locacoes_ativas = cursor.fetchall()
            placas_ocupadas = set()

            for loc_id, placa, loc_inicio, loc_fim, _ in locacoes_ativas:
                if self._periodos_conflitam(data_inicio, data_fim, loc_inicio, loc_fim):
                    placas_ocupadas.add(placa)

            return [v for v in veiculos_categoria if v.placa not in placas_ocupadas]
        except Exception as e:
            print(f"Erro ao buscar veículos disponíveis: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
