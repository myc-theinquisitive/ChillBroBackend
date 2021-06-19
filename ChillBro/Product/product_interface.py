import abc


class ProductInterface(abc.ABC):

    @abc.abstractmethod
    def validate_create_data(self, product_data):
        pass

    @abc.abstractmethod
    def create(self, product_data):
        pass

    @abc.abstractmethod
    def validate_update_data(self, product_data):
        pass

    @abc.abstractmethod
    def update(self, product_data):
        pass

    @abc.abstractmethod
    def get(self, product_id):
        pass

    @abc.abstractmethod
    def get_by_ids(self, product_ids):
        pass


