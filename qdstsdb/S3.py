__author__ = 'rajatv'
from boto.s3.connection import S3Connection
from boto.s3.connection import ProtocolIndependentOrdinaryCallingFormat


class S3Bucket:

    def __init__(self, config, bucket_name):
        self.config = config
        self.bucket_name = bucket_name

        access_key = self.config.get("default", "access_key")
        if access_key is None:
            raise Exception("Access Key is not available through config or command line")

        secret_key = self.config.get("default", "secret_key")
        if secret_key is None:
            raise Exception("Secret Key is not available through config or command line")
        self.connection = S3Connection(access_key, secret_key,
                                       calling_format=ProtocolIndependentOrdinaryCallingFormat())
        self.bucket = self.connection.get_bucket(self.bucket_name)

    def get_path(self, path):
        key = self.bucket.get_key(path)
        return key.get_contents_as_string()

    def path_exists(self, path):
        return self.bucket.get_key(path) is not None

    def write(self, path, contents):
        if self.path_exists(path):
            key = self.bucket.get_key(path)
        else:
            key = self.bucket.new_key(path)

        key.set_contents_from_string(contents)

    def write_file(self, path, filename):
        key = self.bucket.new_key(path)
        fp = open(filename)
        key.set_contents_from_file(fp)
        fp.close()

