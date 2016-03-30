#!/bin/sh

(cd client; ./install_client.sh; ./install_injection.sh)
(cd realtime; ./install_realtime.sh)
(cd backend; ./install_backend.sh)
(cd sniffer; ./install_sniffer.sh)

echo '##########################################################################'
echo "# Don't forget to create your population scripts or update existing ones #"
echo '##########################################################################'
