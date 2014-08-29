#!/bin/bash
#
# This script is to add nfm rules to TCAM of Netronome network flow engine 3240.
# * Only IPv4 traffic is sent to host ports.
# * Total traffic of SEIEE, SJTU, is captured. 
# This script needs root privilege to run.
#
# by chenxm

nfmbin="/opt/netronome/bin"
echo "NFM bin folder: $nfmbin"
cd $nfmbin
echo "Delete all rules"
./rules --deleteall -M

# rules for wifi traffic
# NFM port nfe.0.19
function add_wifi() {
	echo "Add rule rule_wifi to NFM port nfe.0.19"
	./rules -A -n "rule_wifi_src" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_sa=111.186.0.0/18  --host_dest_id=19 -a VIA_HOST -M
	./rules -A -n "rule_wifi_dst" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_da=111.186.0.0/18  --host_dest_id=19 -a VIA_HOST -M
}


# rules for school of SEIEE
# NFM port nfe.0.20
function add_seiee() {
	echo "Add rule rule_dx1 to NFM port nfe.0.20"
	./rules -A -n "rule_dx1_src" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_sa=202.120.36.0/24  --host_dest_id=20 -a VIA_HOST -M
	./rules -A -n "rule_dx1_dst" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_da=202.120.36.0/24  --host_dest_id=20 -a VIA_HOST -M

	echo "Add rule rule_dx2 to NFM port nfe.0.20"
	./rules -A -n "rule_dx2_src" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_sa=202.120.37.0/24  --host_dest_id=20 -a VIA_HOST -M
	./rules -A -n "rule_dx2_dst" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_da=202.120.37.0/24  --host_dest_id=20 -a VIA_HOST -M

	echo "Add rule rule_dx3 to NFM port nfe.0.20"
	./rules -A -n "rule_dx3_src" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_sa=202.120.38.0/24  --host_dest_id=20 -a VIA_HOST -M
	./rules -A -n "rule_dx3_dst" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_da=202.120.38.0/24  --host_dest_id=20 -a VIA_HOST -M

	echo "Add rule rule_dx4 to NFM port nfe.0.20"
	./rules -A -n "rule_dx4_src" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_sa=202.127.242.0/24  --host_dest_id=20 -a VIA_HOST -M
	./rules -A -n "rule_dx4_dst" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_da=202.127.242.0/24  --host_dest_id=20 -a VIA_HOST -M
	
	echo "Add rule rule_dx45 to NFM port nfe.0.20"
	./rules -A -n "rule_dx45_src" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_sa=202.120.39.0/24  --host_dest_id=20 -a VIA_HOST -M
	./rules -A -n "rule_dx45_dst" -p1 -b -k --etype=ETHERTYPE_IP  --ipv4_da=202.120.39.0/24  --host_dest_id=20 -a VIA_HOST -M
}


# rules for HTTP and HTTPS traffic
# NFM port nfe.0.21
function add_rest_http() {
	echo "Add rule all_rest_http_* to NFM port nfe.0.21"
	./rules -A -n "all_rest_http_80" -p 10 -b -k --etype=ETHERTYPE_IP --ipv4_proto=TCP --dport=80 --host_dest_id=21 -a VIA_HOST -M
	./rules -A -n "all_rest_http_3128" -p 10 -b -k --etype=ETHERTYPE_IP --ipv4_proto=TCP --dport=3128 --host_dest_id=21 -a VIA_HOST -M
	./rules -A -n "all_rest_http_8080" -p 10 -b -k --etype=ETHERTYPE_IP --ipv4_proto=TCP --dport=8080 --host_dest_id=21 -a VIA_HOST -M
	./rules -A -n "all_rest_http_8081" -p 10 -b -k --etype=ETHERTYPE_IP --ipv4_proto=TCP --dport=8081 --host_dest_id=21 -a VIA_HOST -M
	./rules -A -n "all_rest_http_9080" -p 10 -b -k --etype=ETHERTYPE_IP --ipv4_proto=TCP --dport=9080 --host_dest_id=21 -a VIA_HOST -M
	./rules -A -n "all_rest_http_8000" -p 10 -b -k --etype=ETHERTYPE_IP --ipv4_proto=TCP --dport=8000 --host_dest_id=21 -a VIA_HOST -M
	./rules -A -n "all_rest_http_8001" -p 10 -b -k --etype=ETHERTYPE_IP --ipv4_proto=TCP --dport=8001 --host_dest_id=21 -a VIA_HOST -M

	echo "Add rule all_rest_https_tcpudp to NFM port nfe.0.21"
	./rules -A -n "all_rest_https_tcp" -p 10 -b -k --etype=ETHERTYPE_IP --ipv4_proto=TCP --dport=443 --host_dest_id=21 -a VIA_HOST -M
	./rules -A -n "all_rest_https_udp" -p 10 -b -k --etype=ETHERTYPE_IP --ipv4_proto=UDP --dport=443 --host_dest_id=21 -a VIA_HOST -M

	# rules for all the rest of traffic
	echo "Add rule all_rest"
	./rules -A -n "all_rest" -p 100 -b --host_dest_id=30 -a VIA_HOST -M
}

# Run commands
add_wifi


echo "Done!"
