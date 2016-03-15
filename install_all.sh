#!/bin/sh

(cd client; ./install_client.sh; ./install_injection.sh)
(cd realtime; ./install_realtime.sh)
(cd backend; ./install_backend.sh)
