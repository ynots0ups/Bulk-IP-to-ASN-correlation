#!/usr/bin/env python
# @ynots0ups
# https://github.com/ynots0ups/Bulk-IP-to-ASN-correlation/

import re
import ipaddress
import time
from bisect import bisect

# Download BGP table
# http://thyme.apnic.net/current/data-raw-table
# http://thyme.apnic.net/current/data-used-autnums

t = time.time()

# Populate subnet mask address count lookup tuple
# NETMASK_MAP[0] = /1, NETMASK_MAP[1] = /2, NETMASK_MAP[2] = /3, ...
NETMASK_MAP = (2147483648,1073741824,536870912,268435456,134217728,67108864,33554432,16777216,8388608,4194304,2097152,1048576,524288,262144,131072,65536,32768,16384,8192,4096,2048,1024,512,256,128,64,32,16,8,4,2,1)

subnet_lookup_table = []
asn_lookup_table = []
asn_table = {}

# Takes filename as input, removes non-valid IPs, and returns a list of uniq first octets of and all full IPs for querying
def build_ips(filename):
	clean_ips = []
	ip_failures = []
	with open(filename) as f:
		ip_list = [line.strip() for line in f]

	# IP Sanitization checks
	ip_pattern = re.compile('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

	uniq_octets = set()
	for ip in ip_list:
		# Remove invalid IP Addresses
		if not ip_pattern.match(ip):
			ip_failures.append(ip)
			continue

		# Remove private, multicast, unspecified, reserved, loopback and link_local addresses
		if ipaddress.ip_network(ip).is_private or ipaddress.ip_network(ip).is_multicast or ipaddress.ip_network(ip).is_unspecified or ipaddress.ip_network(ip).is_reserved or ipaddress.ip_network(ip).is_loopback or ipaddress.ip_network(ip).is_link_local:
			ip_failures.append(ip)
			continue

		clean_ips.append(ip)
		# Extract a unique list of first octets to reduce our search base
		uniq_octets.add(ip.strip().split('.')[0])

	# Print invalid IP addresses to file
	invalid_filename = 'ip2asn-' + str(int(t)) + '-invalids.txt'
	print('[-] Removed ' + str(len(ip_failures)) + ' invalid IP Addresses. Find them in ' + invalid_filename + '.')
	with open(invalid_filename, 'a') as f:
		for ip in ip_failures:
			f.write(str(int(time.time())) + ',' + ip + '\n')

	return clean_ips, uniq_octets

# Takes a IP/CIDR Prefix and construts a hash table of int(max_ip)
def calculate_net_rage(subnet):
	mask = int(subnet.split('/')[1]) # extract mask
	min_ip = ipaddress.ip_address(subnet.split('/')[0]) # provided IP is mininmum in range
	max_ip = int(min_ip + NETMASK_MAP[mask - 1] - 1) # Add value - 1 based on CIDR Prefix using NETMASK_MAP we declared

	return max_ip

# Builds two lookup tables from provided BGP file and a list of uniq first octets from our query IPs
# subnet_lookup_table is a list of maximum addresses, in int format, for each assigned subnet range based on BGP data
# asn_lookup_table is a list of ASNs
# The order of these two tables coincide with one another, allowing for bisection algorithmic application
def build_lookup(filename, uniq_octets):
	with open(filename) as f:
		for line in f:
			# Split netmasks and ASN #s
			split_line = line.strip().split("\t", 1)
			# Check if first octets of netmask are within our input set
			if split_line[0].split('/')[0].split('.')[0] in uniq_octets:
				# Add it to the netmask/asn table
				max_ip = calculate_net_rage(split_line[0])
				subnet_lookup_table.append(max_ip)
				asn_lookup_table.append(split_line[1])

# Builds a table of each ASN number and it's description based on BGP data
def build_asn(filename):
	# Create asn/owner table
	with open(filename) as f:
		for line in f:
			# Split ASN #s and description
			asn = line.strip().split(' ', 1)
			# Add it to the ASN table
			asn_table[asn[0]] = asn[1]

# Perform a bisect Algorithm Function against our data sets for a given IP address, returning the appropriate ASN number
def do_lookup(ip):
	i = bisect(subnet_lookup_table, ip)
	return asn_lookup_table[i]

ip_list, uniq_octets = build_ips('uniq_ip.txt')

build_lookup('data-raw-table', uniq_octets)
build_asn('data-used-autnums')

for ip in ip_list:
	asn = do_lookup(int(ipaddress.ip_address(ip)))
	with open('ip2asn-' + str(int(t)) + '-results.txt', 'a') as f:
		f.write(str(int(time.time())) + ',' + ip + ',' + asn + ',"' + asn_table[asn] + '"\n')

print('====================================================')
print('[+] Complete!\n')
print("This took: " + str(time.time() - t))
