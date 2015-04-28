__author__ = 'rajatv'
import logging
import inspect
import string
import os
import qds_sdk.cluster
from time import sleep
from argparse import ArgumentDefaultsHelpFormatter
from S3 import S3Bucket
from urlparse import urlparse


class Cluster(object):

    cluster_bringup_timeout = 900
    wait_time = 30

    @classmethod
    def setup_parser(cls, global_sub_parser):
        cls.parser = global_sub_parser.add_parser("cluster",
                                                  help="Manage Hbase with OpenTSDB installed on it.")
        cls.sub_parser = cls.parser.add_subparsers()

        cls.create_parser = cls.sub_parser.add_parser("create", help="Create the opentsdb cluster",
                                                      formatter_class=ArgumentDefaultsHelpFormatter)
        cls.create_parser.add_argument("-l", "--label",
                                       default="opentsdb", help="Label for the cluster")
        cls.create_parser.add_argument("-r", "--region",
                                       default="us-east-1", help="AWS Region")
        cls.create_parser.add_argument("-m", "--master-type",
                                       default="c3.xlarge", help="Instance type of master node")
        cls.create_parser.add_argument("-s", "--slave-type",
                                       default="m3.xlarge", help="Instance type of slave node")
        cls.create_parser.add_argument("-n", "--node-bootstrap",
                                       default="opentsdb.sh", help="Name of the node bootstrap file")
        cls.create_parser.add_argument("-k", "--skip", help="Skip some phases of create", default=[],
                                       action="append", choices=["cluster", "s3"])
        cls.create_parser.add_argument("-z", "--s3-location", help="Default S3 location for the account")
        cls.create_parser.add_argument("-o", "--size",
                                       default=2, help="Size of the cluster")

        cls.create_parser.set_defaults(func=cls.create_cmd)

        cls.start_parser = cls.sub_parser.add_parser("start", help="Start the cluster",
                                                     formatter_class=ArgumentDefaultsHelpFormatter)
        cls.start_parser.add_argument("-l", "--label",
                                      default="opentsdb", help="Label for the cluster")
        cls.start_parser.set_defaults(func=cls.start_cmd)

        cls.stop_parser = cls.sub_parser.add_parser("stop", help="Stop the cluster",
                                                    formatter_class=ArgumentDefaultsHelpFormatter)
        cls.stop_parser.add_argument("-l", "--label",
                                     default="opentsdb", help="Label for the cluster")
        cls.stop_parser.set_defaults(func=cls.stop_cmd)

    @classmethod
    def create_cmd(cls, config, args):
        obj = cls(config, args)
        obj.region = args.region
        obj.master_type = args.master_type
        obj.slave_type = args.slave_type
        obj.size = args.size
        obj.node_bootstrap = args.node_bootstrap
        obj.skip = args.skip
        obj.s3_location = args.s3_location
        obj.create()

    @classmethod
    def start_cmd(cls, config, args):
        obj = cls(config, args)
        obj.start()

    @classmethod
    def stop_cmd(cls, config, args):
        obj = cls(config, args)
        obj.stop()

    def __init__(self, config, args):
        self.config = config
        self.label = args.label
        self.base_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

        self.region = None
        self.master_type = None
        self.slave_type = None
        self.size = None
        self.node_bootstrap = None
        self.skip = None
        self.s3_location = None

    def create(self):
        if "cluster" not in self.skip:
            cluster_settings = qds_sdk.cluster.ClusterInfo(
                label=self.label,
                aws_access_key_id=self.config.get("default", "access_key"),
                aws_secret_access_key=self.config.get("default", "secret_key"),
                disallow_cluster_termination=True,
                node_bootstrap_file=self.node_bootstrap
            )

            cluster_settings.set_ec2_settings(
                aws_region='us-east-1'
            )

            cluster_settings.set_hadoop_settings(
                master_instance_type=self.master_type,
                slave_instance_type=self.slave_type,
                initial_nodes=self.size,
                max_nodes=self.size,
                use_hbase=1
            )

            qds_sdk.cluster.Cluster.create(cluster_settings.minimal_payload())

        if "s3" not in self.skip:
            # Parse the s3 url
            url = urlparse(self.s3_location)
            s3 = S3Bucket(self.config, url.netloc)

            #Conf
            copy_src = "%s/../opentsdb/opentsdb.conf" % self.base_path
            conf_file = open(copy_src).read()
            s3.write("%s/scripts/opentsdb/opentsdb.conf"% url.path, conf_file)

            print "*******"
            print url.path
            print url
            print self.s3_location
            print "*******"


            #Node bootstrap
            filein = open(self.base_path + "/../opentsdb/opentsdb.sh")
            src = string.Template(filein.read())
            d = {'s3_location': "%s/scripts/opentsdb" % self.s3_location, 'qdstsdb_version': '0.1'}
            bootstrap = src.safe_substitute(d)

            s3.write("%s/scripts/hadoop/opentsdb.sh"% url.path, bootstrap)

    def start(self):
        qds_sdk.cluster.Cluster.start(self.label)
        cluster_id = qds_sdk.cluster.Cluster.show(self.label)['cluster']['id']
        logging.info("Starting cluster %d with label %s" % (cluster_id, self.label))

        while self.cluster_bringup_timeout > 0:
            logging.info("Cluster %d Status: %s" % (cluster_id, qds_sdk.cluster.Cluster.status(self.label)['state']))
            if qds_sdk.cluster.Cluster.status(self.label)['state'] == 'UP':
                logging.info("Cluster %s is UP and running" % cluster_id)
                break
            self.cluster_bringup_timeout -= self.wait_time
            sleep(self.wait_time)

        if qds_sdk.cluster.Cluster.status(self.label)['state'] != 'UP':
            raise Exception("Cluster %d failed to start" % cluster_id)

    def stop(self):
        qds_sdk.cluster.Cluster.terminate(self.label)
        while qds_sdk.cluster.Cluster.status(self.label)['state'] != 'DOWN':
            sleep(self.wait_time)