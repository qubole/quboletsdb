#!/bin/bash
#Heavily inspired by https://github.com/awslabs/emr-bootstrap-actions/blob/master/opentsdb/install-opentsdb.sh

#For getting node information. For e.g. - is this a master node.
source /usr/lib/hustler/bin/nodeinfo_src.sh

set -e -x
VERSION=2.0.1
NODE_BOOTSTRAP_VERSION=$qdstsdb_version

# Setup Configuration
mkdir -p /media/ephemeral1/opentsdb/tmp
hadoop dfs -get $s3_location/opentsdb.conf /media/ephemeral1/opentsdb/opentsdb.conf

#Check if master
if [ "$_is_master" = "0" ]; then
  exit 0
fi

HBASE_HOME="/usr/lib/hbase"
sudo yum -y install gnuplot
TSD_PACKAGE=opentsdb-${VERSION}.noarch.rpm
TSD_DOWNLOAD=https://github.com/OpenTSDB/opentsdb/releases/download/v${VERSION}/${TSD_PACKAGE}

# download the package and install it
cd /media/ephemeral1/opentsdb
wget --no-check-certificate $TSD_DOWNLOAD
sudo rpm -ivh $TSD_PACKAGE
rm $TSD_PACKAGE

# configure tsd
TSD_HOME=/media/ephemeral1/opentsdb
TSD_INSTALL=/usr/share/opentsdb

# Set tsdb command permission
sudo chmod 755 $TSD_INSTALL/bin/tsdb

# cron to clean the cache directory
cat <<-EOF > $TSD_HOME/clean_cache.sh
#!/bin/bash
sudo /usr/share/opentsdb/tools/clean_cache.sh
EOF
chmod 755 $TSD_HOME/clean_cache.sh
sudo cp $TSD_HOME/clean_cache.sh /etc/cron.daily/

# create a simple script to collect metrics from tsd itself
cat <<-EOF > $TSD_HOME/tsdb-status.sh
#!/bin/bash
echo stats \
 | nc -w 1 localhost 4242 \
 | sed 's/^/put /' \
 | nc -w 1 localhost 4242
EOF

chmod 755 $TSD_HOME/tsdb-status.sh

#
# Only run this script once to initialize TSD.
#
echo "Initializing TSD..."
# check zookeeper connectivity
for i in 1 2 3 4 5 6 7 8 9; do 
  echo "zxcv"
  RUOK=`echo ruok | nc -w 5 localhost 2181`
  echo "Wait for zookeeper"
  if [ "$RUOK" != "imok" ]; then
    echo "Cannot connect to Zookeeper.Retrying"
    sleep 10
  fi
done

echo "qwerty"

if [ "$RUOK" != "imok" ]; then
  echo "Cannot connect to Zookeeper."
  exit 1
fi
# create tables
COMPRESSION=LZO HBASE_HOME=$HBASE_HOME $TSD_INSTALL/tools/create_table.sh


#copy over conf
cp /media/ephemeral1/opentsdb/opentsdb.conf /etc/opentsdb/opentsdb.conf

# start TSD
sudo /etc/init.d/opentsdb start
# wait a while before making tsd metrics
sleep 2
# make tsd metrics
echo stats | nc -w 1 localhost 4242 \
 | awk '{ print $1 }' | sort -u \
 | xargs $TSD_INSTALL/bin/tsdb mkmetric
# put the metrics to tsd every minute
(crontab -l 2>/dev/null; echo "* * * * * $TSD_HOME/tsdb-status.sh > $TSD_HOME/cron.log 2>&1") | crontab -
echo "Completed initializing TSD."
echo "Check the TSD web UI at http://localhost:4242/"

echo "Initializing Graphana"
yum install -y https://grafanarel.s3.amazonaws.com/builds/grafana-2.0.2-1.x86_64.rpm
sudo service grafana-server start

echo "Check the Graphana UI at http://localhost:3000/"