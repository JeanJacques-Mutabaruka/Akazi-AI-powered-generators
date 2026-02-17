"""
AKAZI Job Description Generator V3 - OPTIMISÉ avec leçons apprises
- Helpers réutilisables pour formatage
- Indentations intelligentes (left_indent + first_line_indent)
- Line spacing 1.15 partout
- Paramètres facilement ajustables
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
import json
import yaml
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from utils.akazi_styles import AkaziStyleManager
from utils.akazi_layout import AkaziLayoutManager

class AkaziJobDescGenerator:
    """Générateur Job Description AKAZI - Version optimisée"""
    
    # Font standardisé pour tout le document
    # FONT_NAME = 'Aptos'
    FONT_NAME = 'Century Gothic'
    
    # Couleurs
    COLOR_RED = RGBColor(192, 0, 0)
    COLOR_BLUE = RGBColor(0, 32, 96)
    COLOR_BLACK = RGBColor(0, 0, 0)
    COLOR_ORANGE = RGBColor(255, 140, 0)
    
    # Paramètres de formatage standardisés
    LINE_SPACING_MULTIPLE = 1.15
    
    # Espacements pour titres de sections
    SECTION_TITLE_SPACE_BEFORE = 20
    SECTION_TITLE_SPACE_AFTER = 6
    
    # Espacements pour bullets
    BULLET_SPACE_BEFORE = 3
    BULLET_SPACE_AFTER = 3
    
    # Indentations pour bullets niveau 1
    BULLET_L1_LEFT_INDENT = 1.0  # cm
    BULLET_L1_FIRST_LINE = -0.5  # cm (négatif pour hanging)
    
    # Indentations pour bullets niveau 2
    BULLET_L2_LEFT_INDENT = 1.5  # cm
    BULLET_L2_FIRST_LINE = -0.5  # cm (négatif pour hanging)
    
    def __init__(self, input_file: Path, output_file: Path, lang: str = 'fr', **kwargs):
        self.input_file = input_file
        self.output_file = output_file
        self.lang = lang.lower()
        self.data: Optional[Dict] = None
        self.doc: Optional[Document] = None
    
    # ========================================================================
    # HELPERS POUR FORMATAGE (Leçons apprises !)
    # ========================================================================
    
    def _apply_paragraph_format(self, para, 
                                space_before: int = 0, 
                                space_after: int = 0,
                                left_indent: float = 0.0,
                                first_line_indent: float = 0.0,
                                alignment = WD_ALIGN_PARAGRAPH.JUSTIFY,
                                line_spacing_multiple: float = None):
        """
        Applique format complet à un paragraphe
        
        Args:
            para: Le paragraphe à formater
            space_before: Espace avant en pt
            space_after: Espace après en pt
            left_indent: Indentation gauche en cm
            first_line_indent: Indentation 1ère ligne en cm (négatif pour hanging)
            alignment: Alignement du texte
            line_spacing_multiple: Line spacing (ex: 1.15)
        """
        pf = para.paragraph_format
        
        # Espacements
        pf.space_before = Pt(space_before)
        pf.space_after = Pt(space_after)
        
        # Indentations
        pf.left_indent = Cm(left_indent)
        pf.first_line_indent = Cm(first_line_indent)
        
        # Alignement
        para.alignment = alignment
        
        # Line spacing
        if line_spacing_multiple is None:
            line_spacing_multiple = self.LINE_SPACING_MULTIPLE
        
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = line_spacing_multiple
    
    def _set_line_spacing(self, para, multiple: float = None):
        """Définit line spacing pour un paragraphe"""
        if multiple is None:
            multiple = self.LINE_SPACING_MULTIPLE
        
        pf = para.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = multiple
    
    def _create_section_title(self, text: str, color: RGBColor = None, is_budget: bool = False) -> None:
        """
        Crée un titre de section avec formatage standard
        
        Specs:
        - space_before = 20pt
        - space_after = 6pt
        - left_indent = 0 cm
        - first_line_indent = 0 cm
        - line_spacing = 1.15
        - Color = NOIR par défaut (ROUGE seulement pour BUDGET)
        - Bold, 12pt
        """
        if color is None:
            # NOIR par défaut, ROUGE seulement si c'est le budget
            color = self.COLOR_RED if is_budget else self.COLOR_BLACK
        
        para = self.doc.add_paragraph(style='Heading 3')

        
        # Appliquer formatage section title
        self._apply_paragraph_format(
            para,
            space_before=self.SECTION_TITLE_SPACE_BEFORE,
            space_after=self.SECTION_TITLE_SPACE_AFTER,
            left_indent=0.0,
            first_line_indent=0.0,
            alignment=WD_ALIGN_PARAGRAPH.LEFT
        )
        
        # Texte du titre
        run = para.add_run(text.upper())
        run.font.name = self.FONT_NAME
        run.font.size = Pt(12)
        run.font.color.rgb = color
        run.bold = True
    
    def _add_bullet_level1(self, text: str, bold_prefix: str = '', make_bold: bool = False, color: RGBColor = None) -> None:
        """
        Ajoute un bullet point de niveau 1
        
        Args:
            text: Texte du bullet
            bold_prefix: Préfixe à mettre en gras (ex: "SQL")
            make_bold: Si True, TOUT le texte est en gras (pour section skills)
            color: Couleur du texte
        
        Specs:
        - space_before = 3pt
        - space_after = 3pt
        - left_indent = 1.0 cm
        - first_line_indent = -0.5 cm (hanging)
        - line_spacing = 1.15
        """
        if color is None:
            color = self.COLOR_BLACK
        
        # para = self.doc.add_paragraph(style='List Paragraph 3')
        # para.style = 'List Bullet'
        para = self.doc.add_paragraph(style="Akazi Bullet Level 1")
        AkaziStyleManager.apply_bullet(para, level=0)
        
        # Appliquer formatage bullet niveau 1
        self._apply_paragraph_format(
            para,
            space_before=self.BULLET_SPACE_BEFORE,
            space_after=self.BULLET_SPACE_AFTER,
            left_indent=self.BULLET_L1_LEFT_INDENT,
            first_line_indent=self.BULLET_L1_FIRST_LINE,
            alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        )
        
        # Texte avec préfixe optionnel en gras OU tout en gras
        if bold_prefix:
            # Cas 1: Préfixe en gras (ex: "SQL : description")
            bold_run = para.add_run(bold_prefix + " : ")
            bold_run.font.name = self.FONT_NAME
            bold_run.font.size = Pt(10)
            bold_run.font.color.rgb = color
            bold_run.bold = True
            
            # Retirer le préfixe du texte s'il y est déjà
            rest = text.replace(bold_prefix + " : ", "").replace(bold_prefix + ": ", "")
            normal_run = para.add_run(rest)
            normal_run.font.name = self.FONT_NAME
            normal_run.font.size = Pt(10)
            normal_run.font.color.rgb = color
        else:
            # Cas 2: Texte normal OU tout en gras selon make_bold
            run = para.add_run(text)
            run.font.name = self.FONT_NAME
            run.font.size = Pt(10)
            run.font.color.rgb = color
            run.bold = make_bold  # ✅ GRAS si make_bold=True (section skills)
    
    def _add_bullet_level2(self, text: str, color: RGBColor = None) -> None:
        """
        Ajoute un bullet point de niveau 2 (sub-item)
        
        Specs:
        - space_before = 3pt
        - space_after = 3pt
        - left_indent = 1.5 cm
        - first_line_indent = -0.5 cm (hanging)
        - line_spacing = 1.15
        """
        if color is None:
            color = self.COLOR_BLACK
        
        # para = self.doc.add_paragraph()
        # para.style = 'List Bullet 2'  # Style bullet niveau 2

        para = self.doc.add_paragraph(style="Akazi Bullet Level 2")
        AkaziStyleManager.apply_bullet(para, level=1)
        
        # Appliquer formatage bullet niveau 2
        self._apply_paragraph_format(
            para,
            space_before=self.BULLET_SPACE_BEFORE,
            space_after=self.BULLET_SPACE_AFTER,
            left_indent=self.BULLET_L2_LEFT_INDENT,
            first_line_indent=self.BULLET_L2_FIRST_LINE,
            alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        )
        
        # Texte
        run = para.add_run(text)
        run.font.name = self.FONT_NAME
        run.font.size = Pt(10)
        run.font.color.rgb = color
    
    def _add_paragraph(self, text: str, 
                      bold: bool = False, 
                      color: RGBColor = None,
                      alignment = WD_ALIGN_PARAGRAPH.JUSTIFY) -> None:
        """Ajoute un paragraphe normal avec formatage standard"""
        if color is None:
            color = self.COLOR_BLACK
        
        para = self.doc.add_paragraph()
        
        # Format standard pour paragraphes
        self._apply_paragraph_format(
            para,
            space_before=3,
            space_after=3,
            left_indent=0.0,
            first_line_indent=0.0,
            alignment=alignment
        )
        
        run = para.add_run(text)
        run.font.name = self.FONT_NAME
        run.font.size = Pt(10)
        run.font.color.rgb = color
        run.bold = bold
    
    def _disable_contextual_spacing_for_style(self, style_name: str):
        """
        Désactive 'Don't add space between paragraphs of the same style'
        pour un style donné.
        """
        style = self.doc.styles[style_name]
        pPr = style.element.get_or_add_pPr()

        contextual = pPr.find(qn('w:contextualSpacing'))
        if contextual is not None:
            pPr.remove(contextual)

    def _create_akazi_bullet_level1_style(self):
        styles = self.doc.styles
        
        if "Akazi Bullet Level 1" in styles:
            return
        
        style = styles.add_style("Akazi Bullet Level 1", WD_STYLE_TYPE.PARAGRAPH)
        
        # Basé sur List Paragraph (propre pour les bullets)
        style.base_style = styles["List Paragraph"]
        
        # Police
        style.font.name = self.FONT_NAME
        style.font.size = Pt(10)
        
        # Format paragraphe
        pf = style.paragraph_format
        pf.left_indent = Cm(self.BULLET_L1_LEFT_INDENT)
        pf.first_line_indent = Cm(self.BULLET_L1_FIRST_LINE)
        pf.space_before = Pt(self.BULLET_SPACE_BEFORE)
        pf.space_after = Pt(self.BULLET_SPACE_AFTER)
        
        from docx.enum.text import WD_LINE_SPACING
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        pf.line_spacing = self.LINE_SPACING_MULTIPLE

        self._make_style_visible_in_gallery("Akazi Bullet Level 1", priority=5)
        self._make_style_visible_in_gallery("Akazi Bullet Level 2", priority=5)

    def _make_style_visible_in_gallery(self, style_name: str, priority: int = 1):
        style = self.doc.styles[style_name]
        style_element = style.element

        # qFormat -> style recommandé
        qformat = OxmlElement('w:qFormat')
        style_element.append(qformat)

        # uiPriority -> position dans galerie
        priority_el = OxmlElement('w:uiPriority')
        priority_el.set(qn('w:val'), str(priority))
        style_element.append(priority_el)

        # unhideWhenUsed -> visible après utilisation
        unhide = OxmlElement('w:unhideWhenUsed')
        style_element.append(unhide)


    # ========================================================================
    # MÉTHODES DE GÉNÉRATION DU DOCUMENT
    # ========================================================================
    
    def load_data(self):
        """Charge JSON ou YAML"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            if self.input_file.suffix == '.json':
                self.data = json.load(f)
            else:
                self.data = yaml.safe_load(f)
    
    def validate_data(self):
        """Valide structure Job Description"""
        metadata = self.data.get('document_metadata', {})
        doc_type = metadata.get('document_type')
        format_code = metadata.get('format_code')
        
        if doc_type != 'job_description':
            raise ValueError(f"Wrong document_type: {doc_type}, expected 'job_description'")
        
        if not format_code or 'AKAZI' not in format_code:
            raise ValueError(f"Wrong format_code: {format_code}")
        
        return True
    
    def setup_document(self):
        """Initialize Word document"""
        self.doc = Document()
        
        # Styles
        style_manager = AkaziStyleManager(self.doc)
        style_manager.setup_all_styles()

        # Layout
        layout_manager = AkaziLayoutManager(self.doc)
        layout_manager.setup_header_footer()

        # Style Normal
        style = self.doc.styles['Normal']
        style.font.name = self.FONT_NAME
        style.font.size = Pt(10)
        
        # Marges
        for section in self.doc.sections:
            section.top_margin = Cm(2.54)
            section.bottom_margin = Cm(2.54)
            section.left_margin = Cm(2.54)
            section.right_margin = Cm(2.54)
    
        self._disable_contextual_spacing_for_style('Normal')
        self._disable_contextual_spacing_for_style('List Bullet')
        self._disable_contextual_spacing_for_style('List Bullet 2')
        self._create_akazi_bullet_level1_style()



    def generate_header(self):
        """Génère header de la fiche de poste"""
        # Récupérer titre (nouveau ou ancien format)
        if 'mission_title' in self.data:
            title = self.data.get('mission_title', 'FICHE DE POSTE')
        else:
            job_info = self.data.get('job_information', {})
            title = job_info.get('job_title', 'FICHE DE POSTE')
        
        # Title (RED, bold, 14pt, centered)
        title_para = self.doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Appliquer line spacing
        self._set_line_spacing(title_para)
        
        title_run = title_para.add_run(title.upper())
        title_run.font.name = 'Century Gothic'
        title_run.font.size = Pt(14)
        title_run.font.color.rgb = self.COLOR_BLACK
        title_run.bold = True
        
        # ✅ PAS de paragraphe vide après le header
        # Le budget viendra directement après avec space_before=20
    
    def generate_budget(self):
        """
        Génère section budget - UNE SEULE LIGNE
        
        Format: "BUDGET : [valeur]"
        - Taille 12pt
        - ROUGE
        - Bold
        - Pas de titre séparé !
        """
        budget_data = self.data.get('budget', {})
        
        if not budget_data:
            return
        
        # Récupérer texte budget (nouveau format)
        if 'text' in budget_data:
            budget_text = budget_data.get('text', '')
        else:
            # Ancien format
            daily_rate = budget_data.get('daily_rate', '')
            total_budget = budget_data.get('total_budget', '')
            budget_text = daily_rate if daily_rate else total_budget
        
        # UNE SEULE ligne: "BUDGET : [valeur]"
        para = self.doc.add_paragraph()
        
        # Format paragraphe (comme section title)
        self._apply_paragraph_format(
            para,
            space_before=self.SECTION_TITLE_SPACE_BEFORE,
            space_after=self.SECTION_TITLE_SPACE_AFTER,
            left_indent=0.0,
            first_line_indent=0.0,
            alignment=WD_ALIGN_PARAGRAPH.LEFT
        )
        
        # Texte: "BUDGET : [valeur]" - TOUT EN ROUGE, taille 12pt
        budget_run = para.add_run(f"BUDGET : {budget_text}")
        budget_run.font.name = self.FONT_NAME
        budget_run.font.size = Pt(12)  # ✅ Taille 12pt comme les titres
        budget_run.font.color.rgb = self.COLOR_RED  # ✅ Tout en rouge
        budget_run.bold = True
    
    def _generate_new_format_sections(self):
        """Génère sections depuis description.sections (nouveau format)"""
        description = self.data.get('description', {})
        sections = description.get('sections', [])
        
        for section in sections:
            title = section.get('title', '')
            content = section.get('content', '')
            
            # Ajouter titre de section
            if title:
                self._create_section_title(title)
            
            # Détecter si c'est la section COMPÉTENCES (skills)
            # Variantes possibles: français, anglais, etc.
            is_skills_section = any(keyword in title.upper() for keyword in [
                'COMPÉTENCES',
                'QUALIFICATIONS',
                'SKILLS',
                'REQUIRED SKILLS',
                'COMPETENCIES'
            ])
            
            # Si content est une string (paragraphe)
            if isinstance(content, str):
                # Gérer les termes en gras (bold_terms)
                bold_terms = section.get('formatting', {}).get('bold_terms', [])
                
                if bold_terms:
                    # Créer paragraphe avec bold terms
                    para = self.doc.add_paragraph()
                    
                    # Format paragraphe
                    self._apply_paragraph_format(
                        para,
                        space_before=3,
                        space_after=3,
                        alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
                    )
                    
                    # Split et appliquer bold
                    self._add_text_with_bold_terms(para, content, bold_terms)
                else:
                    # Paragraphe simple
                    self._add_paragraph(content)
            
            # Si content est une liste (bullets)
            elif isinstance(content, list):
                # Passer is_skills_section pour mettre bullets niveau 1 en gras
                self._process_content_list(content, is_skills_section=is_skills_section)
    
    def _add_text_with_bold_terms(self, para, text: str, bold_terms: List[str]):
        """Ajoute texte avec certains termes en gras"""
        # Pour simplifier, on va itérer et chercher les termes
        remaining = text
        
        while remaining:
            # Trouver le prochain terme en gras
            next_term = None
            next_pos = len(remaining)
            
            for term in bold_terms:
                pos = remaining.find(term)
                if pos != -1 and pos < next_pos:
                    next_pos = pos
                    next_term = term
            
            if next_term:
                # Ajouter texte avant le terme
                if next_pos > 0:
                    run = para.add_run(remaining[:next_pos])
                    run.font.name = self.FONT_NAME
                    run.font.size = Pt(10)
                    run.font.color.rgb = self.COLOR_BLACK
                
                # Ajouter terme en gras
                bold_run = para.add_run(next_term)
                bold_run.font.name = self.FONT_NAME
                bold_run.font.size = Pt(10)
                bold_run.font.color.rgb = self.COLOR_BLACK
                bold_run.bold = True
                
                # Continuer avec le reste
                remaining = remaining[next_pos + len(next_term):]
            else:
                # Plus de termes, ajouter le reste
                run = para.add_run(remaining)
                run.font.name = self.FONT_NAME
                run.font.size = Pt(10)
                run.font.color.rgb = self.COLOR_BLACK
                remaining = ""
    
    def _process_content_list(self, content: List, is_skills_section: bool = False):
        """
        Traite une liste de contenu (bullets avec hiérarchie)
        
        Args:
            content: Liste de bullets
            is_skills_section: Si True, les bullets niveau 1 seront en GRAS
        """
        for item in content:
            # Item peut être string ou dict
            if isinstance(item, str):
                # Bullet simple niveau 1
                # Si c'est la section skills, mettre en gras
                self._add_bullet_level1(item, make_bold=is_skills_section)
            
            elif isinstance(item, dict):
                text = item.get('text', '')
                inferred = item.get('inferred', False)
                sub_items = item.get('sub_items', [])
                
                # Couleur selon inferred
                color = self.COLOR_ORANGE if inferred else self.COLOR_BLACK
                
                # Ajouter item principal (niveau 1)
                # Si c'est la section skills, mettre en gras
                self._add_bullet_level1(text, make_bold=is_skills_section, color=color)
                
                # Ajouter sub-items (niveau 2)
                for sub_item in sub_items:
                    if isinstance(sub_item, str):
                        self._add_bullet_level2(sub_item)
                    else:
                        sub_text = sub_item.get('text', '')
                        sub_inferred = sub_item.get('inferred', False)
                        sub_color = self.COLOR_ORANGE if sub_inferred else self.COLOR_BLACK
                        self._add_bullet_level2(sub_text, color=sub_color)
    
    def save_document(self):
        """Save document"""
        self.doc.save(str(self.output_file))
    
    def generate(self):
        """Main generation method"""
        self.load_data()
        self.validate_data()
        self.setup_document()
        
        # Générer header
        self.generate_header()
        
        # Générer budget (juste après header)
        self.generate_budget()
        
        # Détecter le format
        is_new_format = 'description' in self.data and 'sections' in self.data.get('description', {})
        
        if is_new_format:
            # NOUVEAU FORMAT (description.sections)
            self._generate_new_format_sections()
        else:
            # ANCIEN FORMAT (pourrait être ajouté si nécessaire)
            pass
        
        self.save_document()
