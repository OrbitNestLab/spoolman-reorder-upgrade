FROM node:22-bookworm-slim AS frontend
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates patch && rm -rf /var/lib/apt/lists/*
WORKDIR /build
ADD https://api.github.com/repos/Donkie/Spoolman/tarball/bed3f14ee77a3a571d31b14215d54b0b88a7519c /tmp/source.tar.gz
RUN tar -xzf /tmp/source.tar.gz --strip-components=1 -C /build
COPY upstream.patch /tmp/upstream.patch
RUN patch --batch -p1 < /tmp/upstream.patch
WORKDIR /build/client_v2
RUN npm ci && npm run check && npm run build

FROM ghcr.io/donkie/spoolman:0.27.0
LABEL org.opencontainers.image.source="https://github.com/OrbitNestLab/spoolman-reorder-upgrade"
COPY --chown=app:app --from=frontend /build/client_v2/build /home/app/spoolman/client_v2/build
COPY --chown=app:app --from=frontend /build/spoolman/settings.py /home/app/spoolman/spoolman/settings.py
COPY --chown=app:app --from=frontend /build/spoolman/reorder.py /home/app/spoolman/spoolman/reorder.py
COPY --chown=app:app --from=frontend /build/spoolman/api/v1/reorder.py /home/app/spoolman/spoolman/api/v1/reorder.py
COPY --chown=app:app --from=frontend /build/spoolman/api/v1/router.py /home/app/spoolman/spoolman/api/v1/router.py
COPY bambu_eu_catalog.json /opt/reorder/bambu_eu_catalog.json
COPY catalog-source.json /opt/reorder/catalog-source.json
COPY ha_start.py /opt/reorder/ha_start.py
ENV SPOOLMAN_PORT=7912 SPOOLMAN_DIR_DATA=/data/spoolman SPOOLMAN_DIR_BACKUPS=/data/spoolman/backups SPOOLMAN_DIR_LOGS=/data/spoolman/logs SPOOLMAN_DIR_CACHE=/data/spoolman/cache
ENV SPOOLMAN_REORDER_CATALOG=/opt/reorder/bambu_eu_catalog.json
ENTRYPOINT ["python", "/opt/reorder/ha_start.py"]
