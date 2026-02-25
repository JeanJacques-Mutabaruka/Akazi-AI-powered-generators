from docx.shared import Cm
from .base_element import BaseElement


class ImageElement(BaseElement):

    def __init__(self, config):
        self.path = config.get("path")
        self.width_cm = config.get("width_cm")
        self.height_cm = config.get("height_cm")

    def render(self, container):

        p = container.add_paragraph()

        if self.width_cm and self.height_cm:
            p.add_run().add_picture(
                self.path,
                width=Cm(self.width_cm),
                height=Cm(self.height_cm)
            )

        elif self.width_cm:
            p.add_run().add_picture(
                self.path,
                width=Cm(self.width_cm)
            )

        else:
            p.add_run().add_picture(self.path)
