-- Script para criação da tabela de locações (PostgreSQL)
-- Banco: db_lpoo_locadora_veiculos

CREATE TABLE IF NOT EXISTS tb_locacoes (
    loc_id SERIAL PRIMARY KEY,
    vei_placa VARCHAR(7) NOT NULL REFERENCES tb_veiculos(vei_placa),
    loc_data_inicio DATE NOT NULL,
    loc_data_fim DATE,
    loc_status VARCHAR(20) NOT NULL DEFAULT 'reservado',
    loc_estrategia VARCHAR(50) NOT NULL DEFAULT 'CalculoPadraoStrategy',
    loc_valor_total DECIMAL(10, 2),
    CONSTRAINT chk_loc_status CHECK (
        loc_status IN ('reservado', 'locado', 'devolvido', 'cancelado')
    ),
    CONSTRAINT chk_loc_datas CHECK (
        loc_data_fim IS NULL OR loc_data_inicio <= loc_data_fim
    )
);

CREATE INDEX IF NOT EXISTS idx_locacoes_veiculo_status
    ON tb_locacoes (vei_placa, loc_status);

CREATE INDEX IF NOT EXISTS idx_locacoes_periodo
    ON tb_locacoes (loc_data_inicio, loc_data_fim);
