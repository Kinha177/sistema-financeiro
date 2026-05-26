from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QScrollArea, QFrame, QLabel, QLineEdit,
)
from PySide6.QtCore import Qt

from app.views.components.page_header import PageHeader


# ── widgets internos ──────────────────────────────────────────────────────────

class _EntradaItem(QWidget):
    """Uma linha do razonete: data · histórico · valor."""

    def __init__(self, data: str, historico: str, valor: str, par: bool = False) -> None:
        super().__init__()
        bg = "rgba(255,255,255,0.025)" if par else "transparent"
        self.setStyleSheet(f"background-color: {bg};")

        ly = QHBoxLayout(self)
        ly.setContentsMargins(12, 4, 12, 4)
        ly.setSpacing(8)

        lbl_data = QLabel(data)
        lbl_data.setFixedWidth(38)
        lbl_data.setStyleSheet(
            "color: #475569; font-size: 11px; background: transparent;"
        )

        lbl_hist = QLabel(historico)
        lbl_hist.setStyleSheet(
            "color: #94a3b8; font-size: 12px; background: transparent;"
        )

        lbl_val = QLabel(valor)
        lbl_val.setFixedWidth(95)
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_val.setStyleSheet(
            "color: #e2e8f0; font-size: 12px; font-weight: 600; background: transparent;"
        )

        ly.addWidget(lbl_data)
        ly.addWidget(lbl_hist, 1)
        ly.addWidget(lbl_val)


def _hsep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setFrameShadow(QFrame.Shadow.Plain)
    f.setFixedHeight(1)
    f.setStyleSheet("color: #1a1a30; background-color: #1a1a30;")
    return f


def _vsep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.VLine)
    f.setFrameShadow(QFrame.Shadow.Plain)
    f.setFixedWidth(1)
    f.setObjectName("razoneteVSep")
    return f


# ── card em T ─────────────────────────────────────────────────────────────────

class _RazoneteCard(QFrame):
    """Representação em T contábil com cabeçalho, lados D/C, totais e saldo."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("razoneteCard")
        self.setMinimumHeight(340)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(_hsep())
        root.addWidget(self._build_col_labels())
        root.addWidget(_hsep())
        root.addWidget(self._build_body(), 1)
        root.addWidget(_hsep())
        root.addWidget(self._build_totals_row())
        root.addWidget(self._build_saldo_footer())

    # ── construção interna ────────────────────────────────────────────────────

    def _build_header(self) -> QWidget:
        w = QWidget()
        w.setObjectName("razoneteHeader")
        ly = QVBoxLayout(w)
        ly.setContentsMargins(16, 10, 16, 10)
        ly.setSpacing(2)

        self._lbl_codigo = QLabel("")
        self._lbl_codigo.setObjectName("razoneteCodigo")
        self._lbl_codigo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._lbl_nome = QLabel("Selecione uma conta")
        self._lbl_nome.setObjectName("razoneteNome")
        self._lbl_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ly.addWidget(self._lbl_codigo)
        ly.addWidget(self._lbl_nome)
        return w

    def _build_col_labels(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background-color: #0b0b18;")
        ly = QHBoxLayout(w)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(0)

        lbl_d = QLabel("DÉBITO")
        lbl_d.setObjectName("razoneteColLabel")
        lbl_d.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_d.setContentsMargins(0, 8, 0, 8)

        lbl_c = QLabel("CRÉDITO")
        lbl_c.setObjectName("razoneteColLabel")
        lbl_c.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c.setContentsMargins(0, 8, 0, 8)

        ly.addWidget(lbl_d, 1)
        ly.addWidget(_vsep())
        ly.addWidget(lbl_c, 1)
        return w

    def _build_body(self) -> QWidget:
        w = QWidget()
        ly = QHBoxLayout(w)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(0)

        deb_wrap = QWidget()
        self._deb_layout = QVBoxLayout(deb_wrap)
        self._deb_layout.setContentsMargins(0, 4, 0, 4)
        self._deb_layout.setSpacing(0)
        self._deb_layout.addStretch()

        cred_wrap = QWidget()
        self._cred_layout = QVBoxLayout(cred_wrap)
        self._cred_layout.setContentsMargins(0, 4, 0, 4)
        self._cred_layout.setSpacing(0)
        self._cred_layout.addStretch()

        ly.addWidget(deb_wrap, 1)
        ly.addWidget(_vsep())
        ly.addWidget(cred_wrap, 1)
        return w

    def _build_totals_row(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background-color: #0b0b18;")
        ly = QHBoxLayout(w)
        ly.setContentsMargins(0, 0, 0, 0)
        ly.setSpacing(0)

        self._lbl_total_deb = QLabel("R$ 0,00")
        self._lbl_total_deb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_total_deb.setStyleSheet(
            "color: #60a5fa; font-size: 12px; font-weight: 700;"
            " padding: 7px 0; background: transparent;"
        )

        self._lbl_total_cred = QLabel("R$ 0,00")
        self._lbl_total_cred.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_total_cred.setStyleSheet(
            "color: #f87171; font-size: 12px; font-weight: 700;"
            " padding: 7px 0; background: transparent;"
        )

        ly.addWidget(self._lbl_total_deb, 1)
        ly.addWidget(_vsep())
        ly.addWidget(self._lbl_total_cred, 1)
        return w

    def _build_saldo_footer(self) -> QWidget:
        self._saldo_footer = QWidget()
        self._saldo_footer.setStyleSheet(
            "background-color: #13132a; border-radius: 0 0 12px 12px;"
        )
        ly = QHBoxLayout(self._saldo_footer)
        ly.setContentsMargins(18, 12, 18, 12)
        ly.setSpacing(10)

        lbl_titulo = QLabel("SALDO FINAL")
        lbl_titulo.setObjectName("razoneteColLabel")
        ly.addWidget(lbl_titulo)

        self._lbl_badge = QLabel("")
        self._lbl_badge.setStyleSheet(
            "color: #475569; font-size: 10px; font-weight: 700;"
            " background-color: #1a1a30; border-radius: 8px; padding: 2px 8px;"
        )
        self._lbl_badge.setVisible(False)
        ly.addWidget(self._lbl_badge)

        ly.addStretch()

        self._lbl_saldo = QLabel("R$ 0,00")
        self._lbl_saldo.setStyleSheet(
            "color: #a78bfa; font-size: 15px; font-weight: 700; background: transparent;"
        )
        ly.addWidget(self._lbl_saldo)
        return self._saldo_footer

    # ── API pública ───────────────────────────────────────────────────────────

    def set_conta(self, codigo: str, nome: str) -> None:
        self._lbl_codigo.setText(codigo)
        self._lbl_nome.setText(nome)

    def limpar(self) -> None:
        for layout in (self._deb_layout, self._cred_layout):
            while layout.count() > 1:
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        self._lbl_total_deb.setText("R$ 0,00")
        self._lbl_total_cred.setText("R$ 0,00")
        self._lbl_saldo.setText("R$ 0,00")
        self._lbl_saldo.setStyleSheet(
            "color: #a78bfa; font-size: 15px; font-weight: 700; background: transparent;"
        )
        self._lbl_badge.setVisible(False)
        self._saldo_footer.setStyleSheet(
            "background-color: #13132a; border-radius: 0 0 12px 12px;"
        )

    def adicionar_debito(self, data: str, historico: str, valor: str, par: bool = False) -> None:
        self._deb_layout.insertWidget(
            self._deb_layout.count() - 1,
            _EntradaItem(data, historico, valor, par),
        )

    def adicionar_credito(self, data: str, historico: str, valor: str, par: bool = False) -> None:
        self._cred_layout.insertWidget(
            self._cred_layout.count() - 1,
            _EntradaItem(data, historico, valor, par),
        )

    def set_totais(
        self,
        total_deb: str,
        total_cred: str,
        saldo: str,
        saldo_negativo: bool = False,
    ) -> None:
        self._lbl_total_deb.setText(total_deb)
        self._lbl_total_cred.setText(total_cred)
        self._lbl_saldo.setText(saldo)

        if saldo_negativo:
            cor, badge_txt, badge_cor, footer_accent = (
                "#f87171", "CRÉDITO", "#7f1d1d", "rgba(248,113,113,0.12)"
            )
        else:
            cor, badge_txt, badge_cor, footer_accent = (
                "#86efac", "DÉBITO", "#14532d", "rgba(134,239,172,0.10)"
            )

        self._lbl_saldo.setStyleSheet(
            f"color: {cor}; font-size: 15px; font-weight: 700; background: transparent;"
        )
        self._lbl_badge.setText(f"● {badge_txt}")
        self._lbl_badge.setStyleSheet(
            f"color: {cor}; font-size: 10px; font-weight: 700;"
            f" background-color: {badge_cor}; border-radius: 8px; padding: 2px 8px;"
        )
        self._lbl_badge.setVisible(True)
        self._saldo_footer.setStyleSheet(
            f"background-color: #13132a;"
            f" border-top: 2px solid {cor};"
            f" border-radius: 0 0 12px 12px;"
        )


# ── página principal ──────────────────────────────────────────────────────────

class RazoneteView(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = PageHeader("Razonetes", "Representação em T das contas contábeis")
        btn_pdf = QPushButton("Exportar PDF")
        btn_pdf.setObjectName("btnSecondary")
        btn_pdf.setFixedWidth(120)
        header.add_action(btn_pdf)
        root.addWidget(header)

        content = QWidget()
        content.setObjectName("pageContent")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 20, 28, 28)
        cl.setSpacing(14)

        cl.addWidget(self._build_filter_card())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        canvas = QWidget()
        canvas_ly = QVBoxLayout(canvas)
        canvas_ly.setContentsMargins(0, 0, 0, 0)
        canvas_ly.setSpacing(0)

        self._card = _RazoneteCard()
        canvas_ly.addWidget(self._card)
        canvas_ly.addStretch()

        scroll.setWidget(canvas)
        cl.addWidget(scroll, 1)

        root.addWidget(content)

    def _build_filter_card(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        outer = QVBoxLayout(card)
        outer.setContentsMargins(18, 14, 18, 14)
        outer.setSpacing(10)

        # ── linha 1: conta + botão ────────────────────────────────────────────
        row1 = QWidget()
        ly1 = QHBoxLayout(row1)
        ly1.setContentsMargins(0, 0, 0, 0)
        ly1.setSpacing(10)

        lbl = QLabel("CONTA")
        lbl.setObjectName("labelField")
        ly1.addWidget(lbl)

        self._combo_conta = QComboBox()
        self._combo_conta.setPlaceholderText("Selecione a conta…")
        self._combo_conta.setMinimumWidth(300)
        ly1.addWidget(self._combo_conta)

        ly1.addStretch()

        self._btn_consultar = QPushButton("Gerar Razonete")
        self._btn_consultar.setFixedWidth(130)
        ly1.addWidget(self._btn_consultar)

        outer.addWidget(row1)

        # ── linha 2: pesquisa + ordenação ─────────────────────────────────────
        row2 = QWidget()
        ly2 = QHBoxLayout(row2)
        ly2.setContentsMargins(0, 0, 0, 0)
        ly2.setSpacing(10)

        self._edit_pesquisa = QLineEdit()
        self._edit_pesquisa.setPlaceholderText("Pesquisar no histórico…")
        self._edit_pesquisa.setClearButtonEnabled(True)
        ly2.addWidget(self._edit_pesquisa, 1)

        self._btn_ordenar = QPushButton("↑ Data")
        self._btn_ordenar.setObjectName("btnSecondary")
        self._btn_ordenar.setFixedWidth(90)
        self._btn_ordenar.setToolTip("Alternar ordem cronológica")
        ly2.addWidget(self._btn_ordenar)

        outer.addWidget(row2)

        return card
