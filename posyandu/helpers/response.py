class ResponseHelper:
    @staticmethod
    def get_response(status, message, data=None):
        response = {
            'status': status,
            'message': message
        }

        if data is not None:
            response['data'] = data

        return response

    @staticmethod
    def get_already_exist_response(status, type, data=None):
        message = str(type) + ' already exists'
        response = ResponseHelper.get_response(status, message, data)
        return response
