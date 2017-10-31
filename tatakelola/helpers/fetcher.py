from sqlalchemy import func, and_
from tatakelola import db
from tatakelola.models import SdContent, Geojson, Region
from transformer import PemetaanContentTransformer, GeojsonTransformer
import geojson


class TatakelolaFetcher():
    @staticmethod
    def fetch_geojsons():
        subq = db.session.query(SdContent, func.max(SdContent.change_id).label('max_change_id'),
                                func.max(SdContent.id).label('max_id')) \
            .filter(SdContent.type == 'pemetaan') \
            .group_by(SdContent.desa_id) \
            .subquery()

        sd_contents = db.session.query(SdContent) \
            .join(subq, and_(
            SdContent.desa_id == subq.c.desa_id,
            SdContent.type == subq.c.type,
            SdContent.change_id == subq.c.max_change_id,
            SdContent.id == subq.c.max_id)) \
            .all()

        geos = []

        for sd_content in sd_contents:
            region = db.session.query(Region).filter(Region.desa_id == sd_content.desa_id).first()
            if not region:
                continue

            db.session.query(Geojson).filter(Geojson.fk_region_id == region.id).delete()

            contents = PemetaanContentTransformer.transform(sd_content.content)
            for content in contents:
                data = GeojsonTransformer.transform(contents[content])
                geo = Geojson()
                geo.type = content
                geo.data = geojson.dumps(data)
                geo.fk_region_id = region.id
                geos.append(geo)

        db.session.add_all(geos)
        db.session.commit()
