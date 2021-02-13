# Bulk-IP-to-ASN-correlation
Perform a localized mass ASN lookup on a bulk dataset of IP Addresses

## How to use

Download the two BGP datasets linked within the top of the document (http://thyme.apnic.net/current/data-raw-table, and http://thyme.apnic.net/current/data-used-autnums).
The first of these contains all assigned subnet ranges from IANA and their associated ASN numbers.
The second a list of ASN numbers and descriptor.
They are both updated daily between 4am and 9am +10GMT as outlined at http://thyme.apnic.net.
Place these two files, and the list of IPs you wish to lookup named uniq_ip.txt, within the same folder as the ip2asn.py script.
Execute bulk-ip-to-asn-correlation.py
You will be given two output files – ip2asn-<timestamp>-invalids.txt containing a list of all identified invalid IP addresses (including local and reserved addresses) and ip2asn-<timestamp>results.txt containing csv formatted results with a header of timestamp,ip,asn,”asn descriptor”.

## bulk-ip-to-asn-correlation.py

It took me awhile to figure out the most efficient way to perform the correlation between a provided IP address and it’s associated subnet as registered from IANA.

The key to my implementation is explained in the first “Other Examples” at https://docs.python.org/3/library/bisect.html where they associate a letter grade to a test score based on a grading scale.

Note that all of the IP addresses are converted to their integer value for computation.

First, I create a tuple of the total number of IP addresses contained within each CIDR prefix, from a /1 to a /32 and store those in NETMASK_MAP. I think create a clean list of IP addresses that will be looked up from the provided file, filtering out invalid addresses. During this process I also extract a unique list of first octets for our query addresses. This will be utilized to filter out many of the unneeded ranges from the BGP data sets.

Next, I build two lookup tables utilizing the data-raw-table file containing IANA registered subnets and their respective ASNs. For each subnet in the BGP data set, we first determine if the first octet is included in our uniq list of octets from the query IP addresses. If it is, we then compute the max IP address (calculate_net_rage()) in the specified CIDR range. These maximum IPs are added to subnet_lookup_table. A second table, asn_lookup_table, is created in sequence with this containing the corresponding ASN number for each maximum IP address. This follows the grade bisect example where the subnet_lookup_table is the breakpoints variable and asn_lookup_table is the letter grades.

We then build a final table from the data-used-autnums BGP data set which contains a correlation of ASN numbers to their descriptor text.

Finally, for each IP address in our cleaned query list, we perform a bisect as outlined in the linked python documentation to correlate which maximum IP address the given IP falls under and it’s associated ASN number. That is then correlated to the descriptor text.

# Disclaimer
If the IP you provide doesn't exist I have no idea what will happen. It will probably explode. Good luck.
