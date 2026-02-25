
def clean_none(style_dict):
    return {k: v for k, v in style_dict.items() if v is not None}
