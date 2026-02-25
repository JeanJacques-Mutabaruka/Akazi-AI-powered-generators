
class UnitConverter:

    EMU_PER_CM = 360000
    EMU_PER_MM = 36000
    EMU_PER_INCH = 914400

    @staticmethod
    def cm(value):
        return int(value * UnitConverter.EMU_PER_CM)
