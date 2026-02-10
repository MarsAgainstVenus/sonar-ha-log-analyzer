ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Copy files
COPY run.sh /run.sh
COPY analyzer.py /analyzer.py

RUN chmod a+x /run.sh

CMD ["/run.sh"]
