
import pandas as pd

class ExcelConfigLoader:

    @staticmethod
    def load(path):

        header_df = pd.read_excel(path, sheet_name="HEADER")
        footer_df = pd.read_excel(path, sheet_name="FOOTER")

        config = {"header": {}, "footer": {}}

        for df, part in [(header_df, "header"), (footer_df, "footer")]:
            for _, row in df.iterrows():
                zone = row["zone"]
                element = {
                    "type": row["type"],
                    "value": row.get("value"),
                    "style": {
                        "font": row.get("font"),
                        "size": row.get("size"),
                        "bold": row.get("bold")
                    }
                }
                config[part].setdefault(zone, []).append(element)

        return config
