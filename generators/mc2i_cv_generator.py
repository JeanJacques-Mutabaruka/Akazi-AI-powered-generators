"""
MC2I CV Generator V3 — Séparation contenu / header-footer
Hérite de BaseGenerator V3.

CHANGEMENTS V3 :
  ✅ _apply_header_footer() surchargé :
     - Si hf_preset fourni → délégation à HeaderFooterEngine (moteur générique)
     - Sinon → MC2ILayoutManager (comportement V2, données dynamiques)
  ✅ setup_document() ne touche PLUS au header/footer
  ✅ Tous les helpers MC2I préservés identiques à V2
"""

from pathlib import Path
from typing import Dict, Any, List, Optional

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

from generators.base_generator import BaseGenerator
from utils.logger import logger


class MC2ICVGenerator(BaseGenerator):
    """
    Générateur CV au format MC2I (Dossier de Compétences).
    Structure JSON attendue : document_metadata, introduction, professional_experiences
    """

    DEFAULT_FONT = "Lato"
    DEFAULT_SIZE = 10

    def __init__(self, input_file: Path, output_file: Path, **kwargs):
        super().__init__(input_file, output_file, **kwargs)

    # =========================================================================
    # SETUP DOCUMENT
    # =========================================================================

    def setup_document(self):
        """
        Marges MC2I (2.54 cm), police Lato 10pt, texte justifié.
        NE configure PAS le header/footer — délégué à _apply_header_footer().
        """
        self.doc = Document()

        try:
            from utils.akazi_styles import AkaziStyleManager
            AkaziStyleManager(self.doc).setup_all_styles()
        except Exception as e:
            logger.warning("style_manager_skipped", reason=str(e))

        # Police et couleur par défaut MC2I
        normal = self.doc.styles['Normal']
        normal.font.name      = self.DEFAULT_FONT
        normal.font.size      = Pt(self.DEFAULT_SIZE)
        normal.font.color.rgb = self.COLOR_TEXT

        pf = normal.paragraph_format
        pf.alignment    = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.line_spacing = 1.15

        self._set_margins(Cm(2.54))

    def _apply_header_footer(self):
        """
        Surcharge MC2I :
        - Si preset YAML fourni → moteur générique (BaseGenerator)
        - Sinon → MC2ILayoutManager avec données dynamiques (initiales, titre, années)
        """
        # Preset explicite fourni → comportement générique
        if self.hf_preset is not None:
            super()._apply_header_footer()
            return

        # Pas de preset → MC2ILayoutManager natif (données tirées du JSON)
        try:
            from utils.mc2i_layout import MC2ILayoutManager
            MC2ILayoutManager(self.doc, data=self.data).setup_header_footer()
            logger.debug("mc2i_layout_applied")
        except Exception as e:
            logger.warning("mc2i_layout_manager_skipped", reason=str(e))

    # =========================================================================
    # VALIDATE DATA
    # =========================================================================

    def validate_data(self) -> bool:
        required = ['document_metadata', 'introduction', 'professional_experiences']
        missing  = [k for k in required if k not in self.data]
        if missing:
            raise ValueError(f"Clés manquantes dans les données MC2I CV : {missing}")
        fmt = self.data['document_metadata'].get('format_code')
        if fmt != 'MC2I_V1':
            raise ValueError(f"format_code incorrect : '{fmt}' (attendu : 'MC2I_V1')")
        return True

    # =========================================================================
    # GENERATE CONTENT
    # =========================================================================

    def generate_content(self):
        """Pipeline contenu MC2I : header → intro → langues → formation → expertise → expériences"""
        self.generate_header()
        self._add_horizontal_separator()
        self.generate_introduction()
        self._add_horizontal_separator()
        self.generate_languages()
        self._add_horizontal_separator()
        self.generate_education()
        self._add_horizontal_separator()
        self.generate_expertise()
        self._add_horizontal_separator()
        self.generate_experiences()

    # =========================================================================
    # HEADER
    # =========================================================================

    def generate_header(self):
        exp_sum = self.data.get('experience_summary', [])
        title   = exp_sum[0].get('title', 'CONSULTANT') if exp_sum else 'CONSULTANT'

        p_name = self.doc.add_paragraph()
        p_name.alignment = WD_ALIGN_PARAGRAPH.LEFT
        self._make_run(p_name, "CONSULTANT DATA",
                       font="Lato", size=16, color=self.COLOR_TEXT, bold=True)

        p_title = self.doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        self._make_run(p_title, title if title else "DATA ANALYST",
                       font="Lato", size=14, color=self.COLOR_COMPANY, bold=True)

        total_months = sum(e.get('duration_months', 0) for e in exp_sum)
        years        = total_months // 12
        p_exp = self.doc.add_paragraph()
        p_exp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        self._make_run(p_exp, f"{years} années d'expérience",
                       font="Lato", size=10, color=self.COLOR_TEXT)

    # =========================================================================
    # INTRODUCTION
    # =========================================================================

    def generate_introduction(self):
        intro = self.data.get('introduction', {})
        for key in ['experience_summary', 'technical_skills_summary', 'functional_skills_summary']:
            text = intro.get(key, '')
            if text:
                p = self.doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                self._make_run(p, text, font="Lato", size=10, color=self.COLOR_TEXT)

        conclusion = intro.get('conclusion', {})
        conclusion_text = (
            conclusion.get('text', '') if isinstance(conclusion, dict) else str(conclusion)
        )
        if conclusion_text:
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            self._make_run(p, conclusion_text, font="Lato", size=10, color=self.COLOR_TEXT)

    # =========================================================================
    # LANGUES
    # =========================================================================

    def generate_languages(self):
        self._add_mc2i_section_title("LANGUES")
        for lang in self.data.get('languages', []):
            self._add_bullet_item(
                self.doc,
                f"{lang.get('language','')} : {lang.get('level','')}",
                color=self.COLOR_TEXT, font="Lato", size=10
            )

    # =========================================================================
    # FORMATION
    # =========================================================================

    def generate_education(self):
        self._add_mc2i_section_title("FORMATION")
        for edu in self.data.get('education', []):
            self._add_bullet_item(
                self.doc,
                f"{edu.get('year','')} : {edu.get('degree','')} - {edu.get('institution','')}",
                color=self.COLOR_TEXT, font="Lato", size=10
            )

    # =========================================================================
    # EXPERTISE
    # =========================================================================

    def generate_expertise(self):
        self._add_mc2i_section_title("EXPERTISES, OUTILS ET TECHNOLOGIES")
        expertise = self.data.get('expertise', {})
        for exp in expertise.get('expertises', []):
            self._add_bullet_item(self.doc, exp, color=self.COLOR_TEXT, font="Lato", size=10)
        masteries = expertise.get('masteries', [])
        if masteries:
            self._add_bullet_item(self.doc, ', '.join(masteries),
                                   color=self.COLOR_TEXT, font="Lato", size=10)

    # =========================================================================
    # EXPÉRIENCES
    # =========================================================================

    def generate_experiences(self):
        self._add_mc2i_section_title("EXPÉRIENCES PROFESSIONNELLES")
        experiences = self.data.get('professional_experiences', [])
        for idx, exp in enumerate(experiences):
            self._generate_single_experience(exp)
            if idx < len(experiences) - 1:
                self._add_horizontal_separator()

    def _generate_single_experience(self, exp: Dict):
        p_company = self.doc.add_paragraph()
        p_company.alignment = WD_ALIGN_PARAGRAPH.LEFT
        self._make_run(p_company, exp.get('company', 'N/A').upper(),
                       font="Lato", size=14, color=self.COLOR_COMPANY,
                       bold=True, small_caps=True)

        p_title = self.doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        self._make_run(p_title, exp.get('title', 'N/A'),
                       font="Lato", size=14, color=self.COLOR_MISSION,
                       bold=True, small_caps=True)

        period = exp.get('period', {}).get('formatted', 'N/A')
        p_period = self.doc.add_paragraph()
        p_period.alignment = WD_ALIGN_PARAGRAPH.LEFT
        self._make_run(p_period, period, font="Lato", size=10,
                       color=self.COLOR_MISSION, small_caps=True)

        context = exp.get('context', '')
        if context:
            p_ctx = self.doc.add_paragraph()
            p_ctx.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            self._make_run(p_ctx, context, font="Lato", size=10, color=self.COLOR_TEXT)

        p_act_label = self.doc.add_paragraph()
        self._make_run(p_act_label, "Activités :",
                       font="Lato", size=10, color=self.COLOR_TEXT, bold=True)
        for activity in exp.get('activities', []):
            self._add_bullet_item(self.doc, activity,
                                   color=self.COLOR_TEXT, font="Lato", size=10)

        p_dom_label = self.doc.add_paragraph()
        self._make_run(p_dom_label, "Domaines :",
                       font="Lato", size=10, color=self.COLOR_TEXT, bold=True)
        for dom in exp.get('functional_domains', []):
            domain_text = dom.get('domain', '') if isinstance(dom, dict) else str(dom)
            self._add_bullet_item(self.doc, domain_text,
                                   color=self.COLOR_TEXT, font="Lato", size=10)

        p_tech_label = self.doc.add_paragraph()
        self._make_run(p_tech_label, "Environnement technique :",
                       font="Lato", size=10, color=self.COLOR_TEXT, bold=True)

        tech_env   = exp.get('technical_environment', [])
        tech_texts = [
            t.get('technologies', '') if isinstance(t, dict) else str(t)
            for t in tech_env
        ]
        if tech_texts:
            p_tech = self.doc.add_paragraph()
            p_tech.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            self._make_run(p_tech, ', '.join(filter(None, tech_texts)),
                           font="Lato", size=10, color=self.COLOR_TEXT)

    # =========================================================================
    # HELPER SPÉCIFIQUE MC2I
    # =========================================================================

    def _add_mc2i_section_title(self, text: str):
        self._add_section_title(
            text,
            font         = "Lato",
            size         = 12,
            color        = self.COLOR_TEXT,
            bold         = True,
            alignment    = WD_ALIGN_PARAGRAPH.LEFT,
            space_before = 12,
            space_after  = 6,
        )
