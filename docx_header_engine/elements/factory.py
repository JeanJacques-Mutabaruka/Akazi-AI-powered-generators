from .text_element import TextElement
from .field_element import FieldElement
from .horizontal_line_element import HorizontalLineElement
from .image_element import ImageElement
from .inline_group_element import InlineGroupElement
from .floating_image_element import FloatingImageElement


class ElementFactory:

    REGISTRY = {
        "text":            TextElement,
        "field":           FieldElement,
        "horizontal_line": HorizontalLineElement,
        "image":           ImageElement,
        "inline_group":    InlineGroupElement,    # Feature 1: PAGE/NUMPAGES inline
        "floating_image":  FloatingImageElement,  # Feature 2: image flottante
    }

    @classmethod
    def create(cls, config):
        element_type = config.get("type")
        klass = cls.REGISTRY.get(element_type)

        if klass is None:
            available = ", ".join(cls.REGISTRY.keys())
            raise ValueError(
                f"Unknown element type: '{element_type}'. "
                f"Available types: {available}"
            )

        return klass(config)

    @classmethod
    def register(cls, type_name, klass):
        """
        Permet d'enregistrer des types d'éléments personnalisés.
        Usage: ElementFactory.register("qr_code", QRCodeElement)
        """
        cls.REGISTRY[type_name] = klass
