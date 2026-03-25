#!/bin/bash

# Basic Zero Touch Provisioning script
# This script runs during initial device provisioning

# Log start of ZTP
logger -t ZTP "Starting Zero Touch Provisioning script"

# Set hostname
HOSTNAME="ztp-device"
hostnamectl set-hostname $HOSTNAME
logger -t ZTP "Set hostname to $HOSTNAME"

# Update package lists
apt-get update
logger -t ZTP "Updated package lists"

# Install basic utilities
apt-get install -y curl wget net-tools
logger -t ZTP "Installed basic utilities"

# Configure basic networking
cat > /etc/netplan/01-netcfg.yaml << EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: true
EOF

# Apply network configuration
netplan apply
logger -t ZTP "Applied network configuration"

# Log completion
logger -t ZTP "Zero Touch Provisioning script completed"

#CUMULUS-AUTOPROVISIONING