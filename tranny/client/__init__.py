class ClientProvider(object):
    def list(self):
        raise NotImplementedError("list is not implemented")

    def add(self, data, download_dir=None):
        raise NotImplementedError("add is not implemented")
