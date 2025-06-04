# Manage OVH DNS with Terraform

This tool is used the first time you want to manage your existing OVH DNS records with Terraform.

It reads the OVH API to get the existing records, then:

 - generates the Terraform code, separated by record type (one file per type),
 - generates a shell script to import the records into the Terraform state.

# Prerequisites

  - `pip install -r requirements.txt`
  - Export those variables:
    - `export OVH_CONSUMER_KEY="your_consumer_key"`
    - `export OVH_APPLICATION_KEY="your_application_key"`
    - `export OVH_APPLICATION_SECRET="your_application_secret"`

# Usage

 - ./main.py
 - cd files
 - terraform init
 - bash import_records_in_tfstate.sh
 - terraform plan -> Should be "No changes. Your infrastructure matches the configuration."

Congratulations! You can now manage your OVH DNS records with Terraform.

Do not use the OVH web interface to manage your DNS records anymore. Doing so will cause a mismatch between your Terraform state and your OVH DNS records.

# Note

You can generate OVH API credentials on the token creation page:

 - https://api.ovh.com/createToken/index.cgi?GET=/*
