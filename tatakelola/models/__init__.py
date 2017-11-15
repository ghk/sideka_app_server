from base import BaseModel
from apbdes import Apbdes, ApbdesModelSchema
from data import Data, DataModelSchema
from geojson import Geojson, GeojsonModelSchema
from penduduk import Penduduk, PendudukModelSchema, PendudukModelSchemaIso, PendudukReference
from region import Region, RegionModelSchema, RegionCompleteModelSchema
from summary import Summary, SummaryModelSchema
from common.models import SdContent, SdContentSchema, SdDesa, SdDesaSchema,\
    ProgressRecapitulation, ProgressRecapitulationModelSchema