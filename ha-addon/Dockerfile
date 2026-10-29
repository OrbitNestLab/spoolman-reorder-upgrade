ARG BUILD_FROM=2c829f0e/amd64-addon-spoolman:0.27.0-0
FROM ${BUILD_FROM}
COPY spoolman/settings.py /home/app/spoolman/spoolman/settings.py
COPY spoolman/reorder.py /home/app/spoolman/spoolman/reorder.py
COPY spoolman/bambu_eu_catalog.json /home/app/spoolman/spoolman/bambu_eu_catalog.json
COPY spoolman/api/v1/reorder.py /home/app/spoolman/spoolman/api/v1/reorder.py
