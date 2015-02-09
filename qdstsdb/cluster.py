__author__ = 'rajatv'
import logging
import qds_sdk.cluster
from time import sleep
from argparse import ArgumentDefaultsHelpFormatter


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
        cls.create_parser.add_argument("-n", "--size",
                                       default=3, help="Size of the cluster")

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
        obj.node_bootstrap
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

        self.region = None
        self.master_type = None
        self.slave_type = None
        self.size = None
        self.node_bootstrap = None

    def create(self):
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

        if qds_sdk.cluster.Cluster.status(clabel)['state'] != 'UP':
            raise Exception("Cluster %d failed to start" % cluster_id)

    def stop(self):
        qds_sdk.cluster.Cluster.terminate(self.label)
        while qds_sdk.cluster.Cluster.status(self.label)['state'] != 'DOWN':
            sleep(self.wait_time)