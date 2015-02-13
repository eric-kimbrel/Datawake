#! /bin/bash

IMAGE=devenv_datawake
DW_DB=erics_datawake
DW_DB_USER=dw
DW_DB_PASSWORD=memex
DW_DB_HOST=172.21.10.117
DW_DB_PORT=3306
DW_CONN_TYPE=mysql
MY_MOUNT=/Users/ekimbrel/Desktop/labor_example

docker run -it --rm  \
    -e "DW_DB=$DW_DB" \
    -e "DW_DB_USER=$DW_DB_USER" \
    -e "DW_DB_PASSWORD=$DW_DB_PASSWORD" \
    -e "DW_DB_HOST=$DW_DB_HOST" \
    -e "DW_DB_PORT=$DW_DB_PORT" \
    -e "DW_CONN_TYPE=$DW_CONN_TYPE" \
    --volume "$MY_MOUNT:/tmp" \
    --volume /Users/ekimbrel/code/eric-kimbrel-github/Datawake/server/datawake:/usr/local/share/tangelo/web/datawake \
    $IMAGE /bin/bash