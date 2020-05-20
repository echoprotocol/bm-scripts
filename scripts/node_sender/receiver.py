import json


class Receiver(object):
    def __init__(self, web_socket):
        super().__init__()
        self.web_socket = web_socket

    @staticmethod
    def get_positive_result(response, print_log):
        if "result" not in response:
            raise Exception(
                "Need result, but received:\n{}".format(json.dumps(response, indent=4))
            )
        return response

    @staticmethod
    def get_negative_result(response, print_log):
        if print_log:
            print("Error received:\n{}".format(json.dumps(response, indent=4)))
        return response

    def get_response(self, id_response, negative, print_log):
        response = json.loads(self.web_socket.recv())
        if response.get("method") == "notice":
            return self.get_response(id_response, negative, print_log)
        if response.get("id") != id_response:
            raise Exception("Wrong 'id'")
        if negative:
            return self.get_negative_result(response, print_log)
        return self.get_positive_result(response, print_log)
