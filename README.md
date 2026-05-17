# LPOO - 2026-1 - Locadora de Veículos

Este é o projeto base utilizado na disciplina de **Linguagem de Programação Orientada a Objetos (LPOO)** do curso de Ciência da Computação, semestre **2026-1**, ministrada pela **Professora Vanessa**.

O objetivo deste projeto é servir como base prática para a aplicação de conceitos de Orientação a Objetos e Padrões de Projeto (Design Patterns) estudados em sala de aula.

## Atividade EAD — 11/05/2026 (CRUD de Locações)

Implementação da interface gráfica e da lógica de negócio para o CRUD de Locações de Veículos, seguindo o padrão **MVC** com persistência em PostgreSQL via **DAO**.

### Funcionalidades implementadas

- **Modelo `Locacao`**: atributo `status` (`reservado`, `locado`, `devolvido`, `cancelado`) e suporte a estratégia de cálculo (Strategy).
- **`LocacaoDAO`**: CRUD completo, `buscar_por_id` e `buscar_veiculos_disponiveis(data_inicio, data_fim, categoria)`.
- **`LocacaoController`**: regras de negócio (locar, devolver, cancelar, detalhes, reserva e CRUD admin).
- **`JanelaPrincipal`**: menu **Cadastro** (Veículo, Locações Admin) e **Ação** (Locar Veículo).
- **`JanelaLocacaoUsuario`**: listagem operacional com Nova Reserva, Locar, Devolver, Cancelar e Ver Detalhes (botões habilitados conforme o status).
- **`JanelaListagemLocacoes` / `JanelaCadastroLocacao`**: CRUD administrativo irrestrito.
- **`JanelaNovaReserva`**: criação de reserva com filtro de veículos disponíveis por período e categoria.

### Como executar

1. Configure o PostgreSQL com o banco `db_lpoo_locadora_veiculos` (credenciais em `dao/db_config.py`).
2. Execute o script `sql/tb_locacoes.sql` no banco (após ter a tabela `tb_veiculos`).
3. Instale a dependência: `pip install psycopg2-binary`
4. Execute: `python main.py`

## Tutoriais

Os guias práticos para a implementação dos padrões de projeto no sistema da locadora estão disponíveis na pasta `tutoriais/`:

*   [Aula 2 - Factory Method](<tutoriais/aula-2-tutorial--factory--locadora-veiculos.md>)
*   [Aula 3.1 - Strategy](<tutoriais/aula-3-1-tutorial-strategy--locadora-veiculos.md>)
*   [Aula 3.2 - State](<tutoriais/aula-3-2-tutorial-state--locadora-veiculos.md>)
*   [Aula 3.3 - Decorator](<tutoriais/aula-3-3-tutorial-decorator--locadora-veiculos.md>)

---

## Detalhamento de Aprendizado

- **Dificuldades Encontradas:** estruturar a hierarquia de janelas `Toplevel` com `wait_window()` para recarregar listagens; alinhar as regras de habilitação dos botões conforme o status da locação.
- **Como resolvi:** reutilizei o padrão do CRUD de Veículos; centralizei as regras de locar/devolver/cancelar no `LocacaoController`; usei `Treeview` com evento `<<TreeviewSelect>>` para habilitar/desabilitar botões.
- **Principal Aprendizado:** compreendi na prática o fluxo MVC com persistência, o ciclo de vida da locação via `status`, e como o `wait_window()` sincroniza telas pai e filha no Tkinter.

## Declaração de Uso de IA

- [ ] **Nenhuma IA foi utilizada** na elaboração deste código.
- [x] **Utilizei IA** como ferramenta de apoio.
- **Ferramenta(s):** Cursor (Auto / agente Composer)
- **Finalidade:** apoio na implementação do CRUD de locações, esclarecimento de dúvidas surgidas durante o desenvolvimento do código e ajuda para montar o readme.
- **Validação:** Declaro que todo o código gerado foi lido, testado e compreendido.

---

### ⚠️ Aviso - 09 de Março

Hoje, dia **09 de março**, foi trabalhado o conteúdo da aula 3. Durante a aula, foi repassado o material do tutorial referente ao padrão **Strategy** (Tutorial 3.1).

**Tarefa para a próxima aula (16 de março):**
Os alunos devem realizar os tutoriais a seguir e enviá-los através do Google Classroom antes do nosso próximo encontro no dia 16:
*   [Aula 3.2 - State](<tutoriais/aula-3-2-tutorial-state--locadora-veiculos.md>)
*   [Aula 3.3 - Decorator](<tutoriais/aula-3-3-tutorial-decorator--locadora-veiculos.md>)
