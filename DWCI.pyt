import arcpy
from arcpy.sa import *

class Toolbox(object):
    def __init__(self):
        self.label = "DWCI Pro Tools"
        self.alias = "DWCIPro"
        self.tools = [DWCI_Pro]

class DWCI_Pro(object):

    def __init__(self):
        self.label = "DWCI Pro – Depth Weighted Water Capture Index"
        self.description = "Genera índice de captación hídrica ponderado por profundidad"
        self.canRunInBackground = False

    def getParameterInfo(self):

        def R(name, disp):
            return arcpy.Parameter(
                displayName=disp,
                name=name,
                datatype="GPRasterLayer",
                parameterType="Required",
                direction="Input")

        def W(name, disp):
            p = arcpy.Parameter(
                displayName=disp,
                name=name,
                datatype="GPDouble",
                parameterType="Required",
                direction="Input")
            p.value = 1.0
            return p

        p0 = R("twi", "Raster TWI")
        p1 = R("geo", "Raster Geología")
        p2 = R("land", "Raster Uso de Suelo")
        p3 = R("slope", "Raster Pendiente")
        p4 = R("depth", "Raster Profundidad de Pozos")

        p5 = W("w_twi", "Peso TWI (0–5)")
        p6 = W("w_geo", "Peso Geología (0–5)")
        p7 = W("w_land", "Peso Uso de Suelo (0–5)")
        p8 = W("w_slope", "Peso Pendiente (0–5)")
        p9 = W("w_depth", "Peso Profundidad (0–5)")

        p10 = arcpy.Parameter(
            displayName="Raster DWCI",
            name="out",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")

        return [p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10]

    def execute(self, params, messages):

        arcpy.CheckOutExtension("Spatial")
        arcpy.env.overwriteOutput = True

        twi   = Raster(params[0].valueAsText)
        geo   = Raster(params[1].valueAsText)
        land  = Raster(params[2].valueAsText)
        slope = Raster(params[3].valueAsText)
        depth = Raster(params[4].valueAsText)

        w_twi   = float(params[5].value)
        w_geo   = float(params[6].value)
        w_land  = float(params[7].value)
        w_slope = float(params[8].value)
        w_depth = float(params[9].value)

        out = params[10].valueAsText

        def norm(r):
            mn = arcpy.GetRasterProperties_management(r, "MINIMUM").getOutput(0)
            mx = arcpy.GetRasterProperties_management(r, "MAXIMUM").getOutput(0)

            mn = float(str(mn).replace(",", "."))
            mx = float(str(mx).replace(",", "."))

            if mx == mn:
                return Con(IsNull(r), 0, 1)

            return Con(IsNull(r), 0, (r - mn) / (mx - mn))

        dwci = ((norm(twi) * w_twi) +
                (norm(geo) * w_geo) +
                (norm(land) * w_land)) * \
               (norm(slope) * w_slope) * (norm(depth) * w_depth)

        dwci.save(out)

        messages.addMessage("✔ DWCI Pro generado correctamente")
