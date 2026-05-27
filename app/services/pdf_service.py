from __future__ import annotations
from decimal import Decimal
from datetime import date
from pathlib import Path
from typing import Callable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, KeepTogether,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.flowables import BalancedColumns


# ── cores ─────────────────────────────────────────────────────────────────────

_NAVY    = HexColor("#1a2e4a")
_NAVY_MD = HexColor("#2d4a6e")
_ACENTO  = HexColor("#2563eb")
_ALT     = HexColor("#f5f7fa")
_TOTAL   = HexColor("#dce6f0")
_CINZA   = HexColor("#6b7280")
_BRANCO  = colors.white
_PRETO   = colors.black


# ── helpers ───────────────────────────────────────────────────────────────────

def _r(v) -> str:
    """Formata Decimal ou numérico em reais: R$ 1.234,56"""
    if v is None:
        return "R$ 0,00"
    d = Decimal(str(v))
    neg = d < 0
    d = abs(d)
    inteiro, *frac = f"{d:.2f}".split(".")
    dec = frac[0] if frac else "00"
    grupos: list[str] = []
    s = inteiro
    while len(s) > 3:
        grupos.insert(0, s[-3:])
        s = s[:-3]
    grupos.insert(0, s)
    formatted = ".".join(grupos) + "," + dec
    return f"R$ -{formatted}" if neg else f"R$ {formatted}"


def _d(v: date | None) -> str:
    if v is None:
        return ""
    return v.strftime("%d/%m/%Y")


class PDFService:
    """Geração de relatórios em PDF via ReportLab."""

    PAGE_W, PAGE_H = A4

    def __init__(self, empresa_nome: str = "Empresa") -> None:
        self.empresa_nome = empresa_nome
        self._styles = self._init_styles()

    # ── estilos ───────────────────────────────────────────────────────────────

    def _init_styles(self) -> dict[str, ParagraphStyle]:
        base = getSampleStyleSheet()
        def s(name, **kw) -> ParagraphStyle:
            return ParagraphStyle(name, parent=base["Normal"], **kw)

        return {
            "empresa":   s("empresa",   fontSize=14, textColor=_NAVY,    fontName="Helvetica-Bold", spaceAfter=2),
            "titulo":    s("titulo",    fontSize=11, textColor=_NAVY_MD,  fontName="Helvetica-Bold", spaceAfter=4),
            "subtitulo": s("subtitulo", fontSize=9,  textColor=_CINZA,    spaceAfter=6),
            "rodape":    s("rodape",    fontSize=7,  textColor=_CINZA,    alignment=TA_CENTER),
            "normal":    s("normal",    fontSize=8,  textColor=_PRETO),
            "bold":      s("bold",      fontSize=8,  textColor=_PRETO,    fontName="Helvetica-Bold"),
            "center":    s("center",    fontSize=8,  textColor=_PRETO,    alignment=TA_CENTER),
            "right":     s("right",     fontSize=8,  textColor=_PRETO,    alignment=TA_RIGHT),
            "header":    s("header",    fontSize=8,  textColor=_BRANCO,   fontName="Helvetica-Bold", alignment=TA_CENTER),
            "secao":     s("secao",     fontSize=8,  textColor=_NAVY_MD,  fontName="Helvetica-Bold"),
            "total":     s("total",     fontSize=8,  textColor=_NAVY,     fontName="Helvetica-Bold", alignment=TA_RIGHT),
            "razonete_conta": s("razonete_conta", fontSize=8, textColor=_BRANCO, fontName="Helvetica-Bold", alignment=TA_CENTER),
            "razonete_cell":  s("razonete_cell",  fontSize=7, textColor=_PRETO,  alignment=TA_RIGHT),
        }

    # ── doc / header / footer ─────────────────────────────────────────────────

    def _make_on_page(self, titulo: str, subtitulo: str) -> Callable:
        empresa = self.empresa_nome

        def on_page(canvas, doc):
            canvas.saveState()
            w = PDFService.PAGE_W

            # faixa de cabeçalho
            canvas.setFillColor(_NAVY)
            canvas.rect(0, PDFService.PAGE_H - 2.2 * cm, w, 2.2 * cm, fill=1, stroke=0)

            canvas.setFillColor(_BRANCO)
            canvas.setFont("Helvetica-Bold", 12)
            canvas.drawString(1.5 * cm, PDFService.PAGE_H - 1.2 * cm, empresa)
            canvas.setFont("Helvetica-Bold", 9)
            canvas.drawString(1.5 * cm, PDFService.PAGE_H - 1.8 * cm, titulo)
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(w - 1.5 * cm, PDFService.PAGE_H - 1.5 * cm, subtitulo)

            # linha separadora do rodapé
            canvas.setStrokeColor(_ACENTO)
            canvas.setLineWidth(1)
            canvas.line(1.5 * cm, 1.4 * cm, w - 1.5 * cm, 1.4 * cm)

            canvas.setFillColor(_CINZA)
            canvas.setFont("Helvetica", 7)
            canvas.drawString(1.5 * cm, 0.8 * cm,
                              f"Gerado em {date.today().strftime('%d/%m/%Y')}")
            canvas.drawRightString(w - 1.5 * cm, 0.8 * cm,
                                   f"Página {doc.page}")

            canvas.restoreState()

        return on_page

    def _doc(self, destino: Path, titulo: str, subtitulo: str) -> tuple[BaseDocTemplate, Callable]:
        on_page = self._make_on_page(titulo, subtitulo)
        doc = BaseDocTemplate(
            str(destino),
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=3.0 * cm,
            bottomMargin=2.0 * cm,
        )
        frame = Frame(doc.leftMargin, doc.bottomMargin,
                      doc.width, doc.height, id="main")
        doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])
        return doc, on_page

    # ── tabela helper ──────────────────────────────────────────────────────────

    def _tbl(
        self,
        rows: list[list],
        col_widths: list[float],
        extra_cmds: list | None = None,
        has_total_row: bool = False,
    ) -> Table:
        n = len(rows)
        cmds = [
            ("BACKGROUND",  (0, 0), (-1, 0),  _NAVY),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  _BRANCO),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1 if not has_total_row else -2),
             [_BRANCO, _ALT]),
            ("GRID",        (0, 0), (-1, -1), 0.25, HexColor("#d1d5db")),
            ("TOPPADDING",  (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ]
        if has_total_row and n >= 2:
            cmds += [
                ("BACKGROUND", (0, n - 1), (-1, n - 1), _TOTAL),
                ("FONTNAME",   (0, n - 1), (-1, n - 1), "Helvetica-Bold"),
            ]
        if extra_cmds:
            cmds.extend(extra_cmds)
        return Table(rows, colWidths=col_widths, style=TableStyle(cmds), repeatRows=1)

    # ── P(aragraph) helpers ────────────────────────────────────────────────────

    def _p(self, text: str, style: str = "normal") -> Paragraph:
        return Paragraph(str(text), self._styles[style])

    def _ph(self, text: str) -> Paragraph:
        return self._p(text, "header")

    # ══════════════════════════════════════════════════════════════════════════
    # Livro Diário
    # ══════════════════════════════════════════════════════════════════════════

    def gerar_livro_diario(
        self,
        dados: list[dict],
        data_inicio: date,
        data_fim: date,
        destino: Path,
    ) -> Path:
        subtitulo = f"{_d(data_inicio)}  –  {_d(data_fim)}"
        doc, _ = self._doc(destino, "Livro Diário", subtitulo)

        W = doc.width
        c_data   = 2.0 * cm
        c_hist   = W - c_data - 3.0 * cm - 3.0 * cm
        c_deb    = 3.0 * cm
        c_cred   = 3.0 * cm

        story: list = [Spacer(1, 0.2 * cm)]
        header = [self._ph("Data"), self._ph("Histórico"),
                  self._ph("Débito"), self._ph("Crédito")]

        rows = [header]
        total_deb = Decimal("0")
        total_cred = Decimal("0")

        for lanc in dados:
            data_str = _d(lanc.get("data"))
            historico = lanc.get("historico", "")
            for item in lanc.get("itens", []):
                valor = Decimal(str(item.get("valor", 0)))
                conta_deb  = item.get("conta_debito", "")
                conta_cred = item.get("conta_credito", "")
                hist_full  = f"{historico} | D: {conta_deb} / C: {conta_cred}"
                rows.append([
                    self._p(data_str),
                    self._p(hist_full),
                    self._p(_r(valor), "right"),
                    self._p(_r(valor), "right"),
                ])
                total_deb  += valor
                total_cred += valor

        rows.append([
            self._p(""),
            self._p("TOTAIS", "bold"),
            self._p(_r(total_deb),  "total"),
            self._p(_r(total_cred), "total"),
        ])

        story.append(self._tbl(rows, [c_data, c_hist, c_deb, c_cred], has_total_row=True))
        story.append(Spacer(1, 0.5 * cm))

        doc.build(story)
        return destino

    # ══════════════════════════════════════════════════════════════════════════
    # Livro Razão
    # ══════════════════════════════════════════════════════════════════════════

    def gerar_livro_razao(
        self,
        dados: list[dict],
        conta_nome: str,
        destino: Path,
    ) -> Path:
        doc, _ = self._doc(destino, "Livro Razão", conta_nome)
        W = doc.width
        c_data  = 2.2 * cm
        c_hist  = W - c_data - 2.5 * cm - 2.5 * cm - 3.0 * cm
        c_deb   = 2.5 * cm
        c_cred  = 2.5 * cm
        c_saldo = 3.0 * cm

        header = [self._ph("Data"), self._ph("Histórico"),
                  self._ph("Débito"), self._ph("Crédito"), self._ph("Saldo")]
        rows = [header]

        for mov in dados:
            rows.append([
                self._p(_d(mov.get("data"))),
                self._p(mov.get("historico", "")),
                self._p(_r(mov.get("debito")),  "right"),
                self._p(_r(mov.get("credito")), "right"),
                self._p(_r(mov.get("saldo")),   "right"),
            ])

        if dados:
            saldo_final = dados[-1].get("saldo", Decimal("0"))
            rows.append([
                self._p(""), self._p("SALDO FINAL", "bold"),
                self._p(""), self._p(""),
                self._p(_r(saldo_final), "total"),
            ])

        story: list = [
            Spacer(1, 0.2 * cm),
            Paragraph(f"Conta: <b>{conta_nome}</b>", self._styles["titulo"]),
            Spacer(1, 0.3 * cm),
            self._tbl(rows, [c_data, c_hist, c_deb, c_cred, c_saldo], has_total_row=bool(dados)),
        ]

        doc.build(story)
        return destino

    # ══════════════════════════════════════════════════════════════════════════
    # DRE
    # ══════════════════════════════════════════════════════════════════════════

    def gerar_dre(
        self,
        dados: dict,
        data_inicio: date,
        data_fim: date,
        destino: Path,
    ) -> Path:
        subtitulo = f"{_d(data_inicio)}  –  {_d(data_fim)}"
        doc, _ = self._doc(destino, "DRE — Demonstração do Resultado do Exercício", subtitulo)
        W = doc.width
        c_cod  = 2.5 * cm
        c_nome = W - c_cod - 3.5 * cm
        c_val  = 3.5 * cm

        def secao(titulo: str, itens: list[dict], subtotal: Decimal, subtotal_label: str) -> list:
            rows = [[self._ph("Código"), self._ph("Descrição"), self._ph("Valor (R$)")]]
            for item in itens:
                rows.append([
                    self._p(item.get("codigo", "")),
                    self._p(item.get("nome", "")),
                    self._p(_r(item.get("valor")), "right"),
                ])
            rows.append([
                self._p(""), self._p(subtotal_label, "bold"),
                self._p(_r(subtotal), "total"),
            ])
            return [
                Paragraph(titulo, self._styles["secao"]),
                Spacer(1, 0.1 * cm),
                self._tbl(rows, [c_cod, c_nome, c_val], has_total_row=True),
                Spacer(1, 0.4 * cm),
            ]

        story: list = [Spacer(1, 0.2 * cm)]
        story += secao("RECEITAS OPERACIONAIS",
                       dados.get("receitas", []),
                       dados.get("total_receitas", Decimal("0")),
                       "Total de Receitas")
        story += secao("CUSTOS",
                       dados.get("custos", []),
                       dados.get("total_custos", Decimal("0")),
                       "Total de Custos")
        story += secao("DESPESAS OPERACIONAIS",
                       dados.get("despesas", []),
                       dados.get("total_despesas", Decimal("0")),
                       "Total de Despesas")

        # resultado final
        lucro = dados.get("lucro_liquido", Decimal("0"))
        label = "LUCRO LÍQUIDO" if lucro >= 0 else "PREJUÍZO LÍQUIDO"
        cor_lucro = HexColor("#d1fae5") if lucro >= 0 else HexColor("#fee2e2")
        result_rows = [
            [self._ph(""), self._ph(label), self._ph(_r(lucro))],
        ]
        tbl_result = Table(result_rows, colWidths=[c_cod, c_nome, c_val],
                           style=TableStyle([
                               ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
                               ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                               ("FONTSIZE",   (0, 0), (-1, 0), 9),
                               ("TEXTCOLOR",  (0, 0), (-1, 0), _BRANCO),
                               ("TOPPADDING", (0, 0), (-1, -1), 6),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                               ("LEFTPADDING", (0, 0), (-1, -1), 6),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                           ]))
        story.append(tbl_result)

        doc.build(story)
        return destino

    # ══════════════════════════════════════════════════════════════════════════
    # Balanço Patrimonial
    # ══════════════════════════════════════════════════════════════════════════

    def gerar_balanco(
        self,
        dados: dict,
        data_base: date,
        destino: Path,
    ) -> Path:
        doc, _ = self._doc(destino, "Balanço Patrimonial", _d(data_base))
        W = doc.width
        half = (W - 0.6 * cm) / 2   # espaço entre as colunas

        def _build_side(titulo: str, grupos: list[tuple[str, list[dict], Decimal]]) -> Table:
            rows: list[list] = [[self._ph(titulo), self._ph("R$")]]
            for grupo_titulo, itens, subtotal in grupos:
                rows.append([
                    Paragraph(f"<b>{grupo_titulo}</b>", self._styles["secao"]),
                    self._p(""),
                ])
                for item in itens:
                    rows.append([
                        self._p(f"  {item.get('codigo', '')}  {item.get('nome', '')}"),
                        self._p(_r(item.get("valor")), "right"),
                    ])
                rows.append([
                    self._p(f"Total {grupo_titulo}", "bold"),
                    self._p(_r(subtotal), "total"),
                ])
            return rows

        c_desc = half - 3.0 * cm
        c_val  = 3.0 * cm

        ativo_rows = _build_side("ATIVO", [
            ("Ativo",   dados.get("ativo", []),   dados.get("total_ativo", Decimal("0"))),
        ])
        passivo_rows = _build_side("PASSIVO + PL", [
            ("Passivo", dados.get("passivo", []), dados.get("total_passivo", Decimal("0"))),
            ("Patrimônio Líquido", dados.get("pl", []), dados.get("total_pl", Decimal("0"))),
        ])

        def _make_tbl(rows):
            return self._tbl(rows, [c_desc, c_val], has_total_row=True)

        tbl_ativo   = _make_tbl(ativo_rows)
        tbl_passivo = _make_tbl(passivo_rows)

        outer = Table(
            [[tbl_ativo, Spacer(0.6 * cm, 1), tbl_passivo]],
            colWidths=[half, 0.6 * cm, half],
        )

        story: list = [
            Spacer(1, 0.2 * cm),
            outer,
            Spacer(1, 0.5 * cm),
        ]

        if not dados.get("equacao_valida", True):
            story.append(Paragraph(
                "⚠ Equação patrimonial desequilibrada — verifique os lançamentos.",
                ParagraphStyle("alerta", parent=self._styles["normal"],
                               textColor=HexColor("#dc2626"), fontName="Helvetica-Bold"),
            ))

        doc.build(story)
        return destino

    # ══════════════════════════════════════════════════════════════════════════
    # Razonetes
    # ══════════════════════════════════════════════════════════════════════════

    def gerar_razonetes(self, dados: list[dict], destino: Path) -> Path:
        """
        dados: lista de dicts com chaves conta_nome, lado_debito, lado_credito, saldo_final.
        Cada lado_debito/credito: list of {"data", "historico", "valor"}
        """
        doc, _ = self._doc(destino, "Razonetes", "Contas em Forma de T")
        W = doc.width

        story: list = [Spacer(1, 0.2 * cm)]

        razonete_w = (W - 0.8 * cm) / 2

        pairs = [dados[i:i + 2] for i in range(0, len(dados), 2)]
        for pair in pairs:
            cols = []
            for razonete in pair:
                cols.append(self._build_razonete(razonete, razonete_w))
            if len(pair) == 1:
                cols.append(Spacer(razonete_w, 1))
            row_tbl = Table([cols], colWidths=[razonete_w, 0.8 * cm if len(pair) == 2 else razonete_w])
            # fix: always two cells
            row_tbl = Table(
                [[self._build_razonete(pair[0], razonete_w),
                  self._build_razonete(pair[1], razonete_w) if len(pair) > 1 else Spacer(razonete_w, 1)]],
                colWidths=[razonete_w, razonete_w],
            )
            story.append(row_tbl)
            story.append(Spacer(1, 0.6 * cm))

        doc.build(story)
        return destino

    def _build_razonete(self, dados: dict, width: float) -> Table:
        conta_nome = dados.get("conta_nome", "—")
        lado_deb   = dados.get("lado_debito", [])
        lado_cred  = dados.get("lado_credito", [])
        saldo      = dados.get("saldo_final", Decimal("0"))

        # Cabeçalho da conta
        header_row = [
            [Paragraph(conta_nome, self._styles["razonete_conta"])],
        ]
        header_tbl = Table(
            header_row,
            colWidths=[width],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), _NAVY),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]),
        )

        # Corpo em T
        max_rows = max(len(lado_deb), len(lado_cred), 1)
        half_w = (width - 0.05 * cm) / 2

        body_rows: list[list] = [
            [self._ph("Débito"), self._ph("Crédito")],
        ]
        for i in range(max_rows):
            deb  = lado_deb[i]["valor"]  if i < len(lado_deb)  else ""
            cred = lado_cred[i]["valor"] if i < len(lado_cred) else ""
            body_rows.append([
                self._p(_r(deb)  if deb  != "" else "", "right"),
                self._p(_r(cred) if cred != "" else "", "right"),
            ])

        # linha de saldo
        body_rows.append([
            self._p("Saldo", "bold"),
            self._p(_r(saldo), "total"),
        ])

        body_cmds = [
            ("LINEAFTER",  (0, 0), (0, -1), 1, _NAVY_MD),
            ("BACKGROUND", (0, 0), (-1, 0), _NAVY_MD),
            ("TEXTCOLOR",  (0, 0), (-1, 0), _BRANCO),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), _TOTAL),
            ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [_BRANCO, _ALT]),
            ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#d1d5db")),
        ]
        body_tbl = Table(body_rows, colWidths=[half_w, half_w],
                         style=TableStyle(body_cmds))

        container = Table(
            [[header_tbl], [body_tbl]],
            colWidths=[width],
            style=TableStyle([
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]),
        )
        return container

    # ══════════════════════════════════════════════════════════════════════════
    # Plano de Contas
    # ══════════════════════════════════════════════════════════════════════════

    def gerar_plano_contas(self, dados: list[dict], destino: Path) -> Path:
        doc, _ = self._doc(destino, "Plano de Contas", "")
        W = doc.width
        c_cod    = 2.5 * cm
        c_nome   = W - c_cod - 2.5 * cm - 2.5 * cm
        c_tipo   = 2.5 * cm
        c_nat    = 2.5 * cm

        header = [self._ph("Código"), self._ph("Nome"),
                  self._ph("Tipo"), self._ph("Natureza")]
        rows = [header]
        for conta in dados:
            rows.append([
                self._p(conta.get("codigo", "")),
                self._p(conta.get("nome", "")),
                self._p(conta.get("tipo", ""), "center"),
                self._p(conta.get("natureza", ""), "center"),
            ])

        story: list = [Spacer(1, 0.2 * cm),
                       self._tbl(rows, [c_cod, c_nome, c_tipo, c_nat])]
        doc.build(story)
        return destino

    # ══════════════════════════════════════════════════════════════════════════
    # Estoque / PEPS-UEPS
    # ══════════════════════════════════════════════════════════════════════════

    def gerar_relatorio_estoque(self, dados: list[dict], destino: Path) -> Path:
        doc, _ = self._doc(destino, "Relatório de Estoque", "Posição atual")
        W = doc.width
        c_nome   = W - 3.0 * cm - 3.0 * cm
        c_estoque = 3.0 * cm
        c_val     = 3.0 * cm

        header = [self._ph("Produto"), self._ph("Estoque"), self._ph("Valor Médio")]
        rows   = [header]
        for item in dados:
            rows.append([
                self._p(item.get("nome", "")),
                self._p(str(item.get("estoque", "")), "right"),
                self._p(_r(item.get("valor_medio")), "right"),
            ])

        story: list = [Spacer(1, 0.2 * cm),
                       self._tbl(rows, [c_nome, c_estoque, c_val])]
        doc.build(story)
        return destino

    def gerar_ficha_peps_ueps(
        self,
        dados: list[dict],
        produto_nome: str,
        metodo: str,
        destino: Path,
    ) -> Path:
        doc, _ = self._doc(destino, f"Custeio {metodo}", produto_nome)
        W = doc.width
        c_data  = 2.2 * cm
        c_lote  = 1.5 * cm
        c_qty   = 2.2 * cm
        c_unit  = 3.0 * cm
        c_total = W - c_data - c_lote - c_qty - c_unit

        header = [self._ph("Data"), self._ph("Lote"), self._ph("Qtde"),
                  self._ph("Valor Unit."), self._ph("Valor Total")]
        rows   = [header]
        grand_total = Decimal("0")
        for i, lote in enumerate(dados, 1):
            vt = Decimal(str(lote.get("valor_total", 0)))
            grand_total += vt
            rows.append([
                self._p(_d(lote.get("data"))),
                self._p(str(i), "center"),
                self._p(str(lote.get("quantidade", "")), "right"),
                self._p(_r(lote.get("valor_unitario")), "right"),
                self._p(_r(vt), "right"),
            ])
        rows.append([
            self._p(""), self._p(""), self._p(""),
            self._p("TOTAL", "bold"),
            self._p(_r(grand_total), "total"),
        ])

        story: list = [
            Spacer(1, 0.2 * cm),
            Paragraph(f"Produto: <b>{produto_nome}</b>  |  Método: <b>{metodo}</b>",
                      self._styles["titulo"]),
            Spacer(1, 0.3 * cm),
            self._tbl(rows, [c_data, c_lote, c_qty, c_unit, c_total], has_total_row=True),
        ]
        doc.build(story)
        return destino

