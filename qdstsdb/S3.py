##
 # Copyright (c) 2015. Qubole Inc
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 #     http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 #    limitations under the License.
##
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

    def write_file(self, filename, path):
        key = self.bucket.new_key(path)
        fp = open(filename)
        key.set_contents_from_file(fp)
        fp.close()
