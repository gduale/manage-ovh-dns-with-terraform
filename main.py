#!/usr/bin/env python3

import os
import sys
import json
import re
import ovh

# Variables
OVH_CONSUMER_KEY = os.getenv("OVH_CONSUMER_KEY")
OVH_APPLICATION_KEY = os.getenv("OVH_APPLICATION_KEY")
OVH_APPLICATION_SECRET = os.getenv("OVH_APPLICATION_SECRET")
OVH_ENDPOINT = "ovh-eu" # Endpoint of API OVH (List of available endpoints: https://github.com/ovh/python-ovh#2-configure-your-application)
zoneName="example.com"
zoneNameUnderscore = zoneName.replace(".", "_")
i = 0

# Check if all variables are set
if not OVH_CONSUMER_KEY or not OVH_APPLICATION_KEY or not OVH_APPLICATION_SECRET or not OVH_ENDPOINT:
    print("Please set all variables")
    exit(1)

# Create directory "files" and build provider.tf into it
if not os.path.exists("files"):
    os.makedirs("files")
if not os.path.exists("files/provider.tf"):
    with open("files/provider.tf", "w") as f:
        f.write("""terraform {
  required_providers {
    ovh = {
      source = "ovh/ovh"
    }
  }
}

provider "ovh" {
  endpoint      = "%s"
}""" % OVH_ENDPOINT)


# Instantiate an OVH Client.
client = ovh.Client(
	endpoint=OVH_ENDPOINT, 
	application_key=OVH_APPLICATION_KEY,
	application_secret=OVH_APPLICATION_SECRET,
	consumer_key=OVH_CONSUMER_KEY,
)

result = client.get(f"/domain/zone/{zoneName}/record")

# Loop on API results and open files for writing
for recordId in result:
    record = client.get(f"/domain/zone/{zoneName}/record/{recordId}")
    if record['fieldType'] == 'A':
        tf_file = f"files/ovh.dns.a.{zoneName}.tf"
    if record['fieldType'] == 'MX':
        tf_file = f"files/ovh.dns.mx.{zoneName}.tf"
    if record['fieldType'] == 'TXT':
        tf_file = f"files/ovh.dns.txt.{zoneName}.tf"
    if record['fieldType'] == 'SPF':
        tf_file = f"files/ovh.dns.spf.{zoneName}.tf"
    if record['fieldType'] == 'DKIM':
        tf_file = f"files/ovh.dns.dkim.{zoneName}.tf"
    if record['fieldType'] == 'DMARC':
        tf_file = f"files/ovh.dns.dmarc.{zoneName}.tf"
    if record['fieldType'] == 'CNAME':
        tf_file = f"files/ovh.dns.cname.{zoneName}.tf"
    if record['fieldType'] == 'NS':
        tf_file = f"files/ovh.dns.ns.{zoneName}.tf"
    if record['fieldType'] == 'SRV':
        tf_file = f"files/ovh.dns.srv.{zoneName}.tf"

    with open(tf_file, "a") as tf_file:
        # Prepare the target value depending on the quotes
        if record['target'].startswith('"') and record['target'].endswith('"'):
            target_content = record['target'][1:-1]  # Remove the quotes at the beginning and end
            target_value = f'"\\"' + target_content + '\\""'  # Add escaped quotes
        else:
            target_value = f'"{record["target"]}"'
            
        terraform_config = f"""resource "ovh_domain_zone_record" "{zoneNameUnderscore}_{i}" {{
    zone      = "{record['zone']}"
    subdomain = "{record['subDomain']}"
    fieldtype = "{record['fieldType']}"
    ttl       = {record['ttl']}
    target    = {target_value}
    # Info: id is "{record['id']}"
}}
"""
        tf_file.write(terraform_config)
        tf_file.write("\n")

    with open("files/import_records_in_tfstate.sh", "a") as shell_file:
        shell_script = f"terraform import ovh_domain_zone_record.{zoneNameUnderscore}_{i} {record['id']}.{zoneName}"
        shell_file.write(shell_script)
        shell_file.write("\n")
    i += 1
    print(f"Record {i}/{len(result)} generated.")

print("Check the README.md file for the next steps.")
