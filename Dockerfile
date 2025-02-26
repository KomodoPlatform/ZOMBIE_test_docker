FROM deckersu/komodoocean AS komodod-builder
FROM ubuntu:20.04

SHELL ["/bin/bash", "-c"]

WORKDIR /data

# Install runtime dependencies required by Komodo
RUN set -euxo pipefail \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get -y --no-install-recommends install \
       ca-certificates curl libgomp1 python3 python3-pip \
       libcurl4-openssl-dev build-essential python3-dev \
       gcc g++ make pkg-config libssl-dev \
    && apt-get -y clean \
    && rm -rf /var/{lib/apt/lists/*,cache/apt/archives/*.deb,tmp/*,log/*} /tmp/*

VOLUME ["/data"]
# Copy komodod, komodo-cli, and fetch-params.sh from the builder stage
COPY --from=komodod-builder /app/komodod /app/komodo-cli /app/fetch-params.sh /data/

RUN pip3 install setuptools wheel slick-bitcoinrpc \
    && apt-get -y clean \
    && rm -rf /var/{lib/apt/lists/*,cache/apt/archives/*.deb,tmp/*,log/*} /tmp/*

EXPOSE 7000

COPY start_blockchain.py /data/

CMD python3 -u start_blockchain.py
