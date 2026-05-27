# SisGest Financeiro

Sistema de gestão financeira e contábil para pequenas e médias empresas, desenvolvido em Python com interface gráfica nativa.

## Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| **Plano de Contas** | Cadastro hierárquico de contas contábeis (ANALITICA / SINTETICA) |
| **Lançamentos** | Registro de lançamentos em partidas dobradas |
| **Livro Diário** | Visualização cronológica dos lançamentos |
| **Livro Razão** | Movimentações por conta com saldo acumulado |
| **Razonetes** | Contas em forma de T com filtro e ordenação |
| **DRE** | Demonstração do Resultado do Exercício por período |
| **Balanço Patrimonial** | Ativo, Passivo e Patrimônio Líquido com equação de validação |
| **Estoque** | Controle de entrada, saída e custeio PEPS/UEPS |
| **Relatórios PDF** | Exportação de todos os relatórios em PDF (ReportLab) |
| **Exportação Excel** | Exportação de todos os relatórios em .xlsx (openpyxl) |

## Tecnologias

- **Python 3.11+**
- **PySide6** (Qt6) — interface gráfica nativa
- **SQLAlchemy 2** + **SQLite** — persistência local
- **Alembic** — migrations de banco de dados
- **ReportLab** — geração de PDFs
- **openpyxl** — exportação para Excel

## Pré-requisitos

- Python 3.11 ou superior
- pip (incluído no Python)
- Windows 10/11 (ou Linux/macOS com Python e Qt instalados)

## Instalação (desenvolvimento)

```powershell
# 1. Clone o repositório
git clone <url-do-repositorio>
cd sistema-financeiro

# 2. Crie o ambiente virtual
python -m venv venv

# 3. Ative o ambiente virtual
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate          # Linux/macOS

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Execute a aplicação
python main.py
```

Na primeira execução o banco de dados `data/sisgest.db` é criado automaticamente via Alembic.

## Testes

```powershell
pytest tests/ -v
```

Os testes usam SQLite em memória — nenhuma configuração adicional é necessária.

### Cobertura atual

| Arquivo de teste | Módulo testado |
|-----------------|----------------|
| `test_estoque.py` | `EstoqueService` — entrada, saída, saldo |
| `test_peps.py` | `EstoqueService.calcular_peps` (FIFO) |
| `test_ueps.py` | `EstoqueService.calcular_ueps` (LIFO) |
| `test_livro_razao.py` | `LivroRazaoService` |
| `test_razonete.py` | `RazoneteService` |
| `test_dre.py` | `DreService` |
| `test_balanco.py` | `BalancoService` |

## Geração do Executável

Para distribuir a aplicação sem exigir Python instalado:

```powershell
# Build padrão
.\build.ps1

# Limpar builds anteriores antes de compilar
.\build.ps1 -Clean
```

O executável é gerado em `dist\SisGestFinanceiro\SisGestFinanceiro.exe`.  
Para distribuir, compacte a pasta `dist\SisGestFinanceiro\` em um arquivo `.zip`.

### Requisitos para o build

- `PyInstaller >= 6.0` (instalado automaticamente pelo `build.ps1` se ausente)
- Todas as dependências do `requirements.txt` instaladas no `venv`

## Estrutura do Projeto

```
sistema-financeiro/
├── main.py                     # Ponto de entrada
├── requirements.txt
├── sisfinanceiro.spec           # Configuração PyInstaller
├── build.ps1                   # Script de build (Windows)
├── alembic.ini
├── alembic/
│   └── versions/               # Migrations do banco de dados
├── app/
│   ├── database/
│   │   ├── base.py             # DeclarativeBase do SQLAlchemy
│   │   └── connection.py       # Engine, Session, init_db()
│   ├── models/                 # ORM models (SQLAlchemy)
│   ├── services/               # Lógica de negócio
│   │   ├── estoque_service.py  # PEPS / UEPS / movimentações
│   │   ├── dre_service.py
│   │   ├── balanco_service.py
│   │   ├── livro_razao_service.py
│   │   ├── razonete_service.py
│   │   ├── plano_contas_service.py
│   │   ├── pdf_service.py      # Geração de PDFs (ReportLab)
│   │   └── excel_service.py    # Exportação Excel (openpyxl)
│   ├── controllers/            # Ligação View ↔ Service
│   ├── views/                  # Widgets PySide6
│   │   └── components/         # Componentes reutilizáveis
│   ├── utils/
│   │   ├── formatters.py       # Formatação BR (moeda, data, CNPJ)
│   │   └── validators.py       # Validação (CNPJ, período, valor)
│   └── exceptions.py           # ValidacaoError
├── assets/
│   └── styles/
│       └── dark_theme.qss      # Tema escuro Qt
├── data/                       # Criado automaticamente (gitignored)
│   └── sisgest.db
└── tests/
```

## Configuração do banco de dados

O banco SQLite é criado em `data/sisgest.db` na primeira execução.  
Para resetar completamente o banco, basta apagar o arquivo e reiniciar a aplicação.

Para ambientes de desenvolvimento que precisam recriar o schema:

```powershell
# Apagar banco existente
Remove-Item data\sisgest.db -ErrorAction SilentlyContinue

# Rodar a aplicação (recria via alembic upgrade head)
python main.py
```

## Utilitários

### Formatação (`app/utils/formatters.py`)

```python
from app.utils.formatters import formatar_moeda, formatar_numero, moeda_para_decimal

formatar_moeda(Decimal("1234.56"))    # "R$ 1.234,56"
formatar_numero(Decimal("1234.56"))   # "1.234,56"
moeda_para_decimal("R$ 1.234,56")    # Decimal("1234.56")
```

### Validação (`app/utils/validators.py`)

```python
from app.utils.validators import validar_cnpj, validar_data_periodo

validar_cnpj("11.222.333/0001-81")       # True/False
validar_data_periodo(date(2024,1,1), date(2024,12,31))  # True
```
