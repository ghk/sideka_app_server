from marshmallow import fields, utils
import warnings
from datetime import datetime


def custom_datetime_deserialize(value):
    try:
        return datetime.strptime(value, '%d/%m/%Y')
    except (TypeError, AttributeError, ValueError):
        return None


class CustomDateTime(fields.DateTime):
    DATEFORMAT_SERIALIZATION_FUNCS = fields.DateTime.DATEFORMAT_SERIALIZATION_FUNCS.copy()
    DATEFORMAT_DESERIALIZATION_FUNCS = fields.DateTime.DATEFORMAT_DESERIALIZATION_FUNCS.copy()

    DATEFORMAT_DESERIALIZATION_FUNCS['keuangan'] = custom_datetime_deserialize

    def _deserialize(self, value, attr, data):
        self.dateformat = self.dateformat or self.DEFAULT_FORMAT
        func = self.DATEFORMAT_DESERIALIZATION_FUNCS.get(self.dateformat)
        if func:
            try:
                return func(value)
            except (TypeError, AttributeError, ValueError):
                raise self.fail('invalid')
        elif self.dateformat:
            try:
                return datetime.strptime(value, self.dateformat)
            except (TypeError, AttributeError, ValueError):
                raise self.fail('invalid')
        elif utils.dateutil_available:
            try:
                return utils.from_datestring(value)
            except TypeError:
                raise self.fail('invalid')
        else:
            warnings.warn('It is recommended that you install python-dateutil '
                          'for improved datetime deserialization.')
            raise self.fail('invalid')
