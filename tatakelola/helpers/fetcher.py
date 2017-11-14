from sqlalchemy import func, and_
from tatakelola import db
from tatakelola.models import Region, SdContent, Geojson, Data
from transformer import ContentTransformer, PemetaanContentTransformer, GeojsonTransformer

import simplejson as json


class TatakelolaFetcher():
    @staticmethod
    def get_content(type, subtype, desa_ids=None):
        subq = db.session.query(SdContent, func.max(SdContent.change_id).label('max_change_id'),
                                func.max(SdContent.id).label('max_id')) \
            .filter(SdContent.type == type) \
            .filter(SdContent.subtype == subtype)

        if (desa_ids):
            subq = subq.filter(SdContent.desa_id.in_(desa_ids))

        subq = subq.group_by(SdContent.desa_id).subquery()

        sd_contents = db.session.query(SdContent) \
            .join(subq, and_(
            SdContent.desa_id == subq.c.desa_id,
            SdContent.type == subq.c.type,
            SdContent.change_id == subq.c.max_change_id,
            SdContent.id == subq.c.max_id)) \
            .all()

        return sd_contents

    @staticmethod
    def fetch_geojsons():
        sd_contents = TatakelolaFetcher.get_content('pemetaan', None)
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
                geo.data = data
                geo.fk_region_id = region.id
                geos.append(geo)

        db.session.add_all(geos)
        db.session.commit()

    @staticmethod
    def fetch_data():
        regions = db.session.query(Region).filter(Region.is_lokpri == True).all()
        desa_ids = [region.desa_id for region in regions]

        sd_contents = TatakelolaFetcher.get_content('penduduk', None, desa_ids)

        for sd_content in sd_contents:
            region = db.session.query(Region).filter(Region.desa_id == sd_content.desa_id).first()
            if not region:
                continue

            db.session.query(Data).filter(Data.fk_region_id == region.id).delete()
            contents = ContentTransformer.transform(sd_content.content)
            if (contents is None):
                continue

            data = Data()
            data.data = { 'penduduk': contents['penduduk'] }
            data.fk_region_id = region.id
            db.session.add(data)

        db.session.commit()
