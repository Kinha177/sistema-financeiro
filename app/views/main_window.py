from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QStatusBar
from PySide6.QtCore import Qt

from app.views.sidebar import Sidebar
from app.views.dashboard_view import DashboardView
from app.views.plano_contas_view import PlanoContasView
from app.views.lancamentos_view import LancamentosView
from app.views.livro_diario_view import LivroDiarioView
from app.views.livro_razao_view import LivroRazaoView
from app.views.razonete_view import RazoneteView
from app.views.dre_view import DreView
from app.views.balanco_view import BalancoView
from app.views.estoque_view import EstoqueView
from app.views.relatorios_view import RelatoriosView
from app.views.configuracoes_view import ConfiguracoesView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SisGest — Gestão Financeira e Contábil")
        self.setMinimumSize(1100, 680)
        self.resize(1440, 860)
        self._setup_ui()
        self._setup_statusbar()

    def _setup_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.navigation_changed.connect(self._on_navigate)
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("contentStack")
        layout.addWidget(self.stack)

        self._register_views()

    def _register_views(self) -> None:
        self._views: dict[str, QWidget] = {
            "dashboard":     DashboardView(),
            "plano_contas":  PlanoContasView(),
            "lancamentos":   LancamentosView(),
            "livro_diario":  LivroDiarioView(),
            "livro_razao":   LivroRazaoView(),
            "razonete":      RazoneteView(),
            "dre":           DreView(),
            "balanco":       BalancoView(),
            "estoque":       EstoqueView(),
            "relatorios":    RelatoriosView(),
            "configuracoes": ConfiguracoesView(),
        }
        for view in self._views.values():
            self.stack.addWidget(view)

    def _setup_statusbar(self) -> None:
        bar = QStatusBar()
        bar.showMessage("Pronto  •  Banco de dados conectado")
        self.setStatusBar(bar)

    def _on_navigate(self, key: str) -> None:
        view = self._views.get(key)
        if view:
            self.stack.setCurrentWidget(view)
