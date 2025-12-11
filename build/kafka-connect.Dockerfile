FROM confluentinc/cp-kafka-connect:7.6.0

# Install Iceberg connector
RUN confluent-hub install --no-prompt iceberg/iceberg-kafka-connect:1.9.2

# Create plugin dir and add required jars
RUN mkdir -p /usr/share/confluent-hub-components/iceberg-iceberg-kafka-connect/lib

WORKDIR /usr/share/confluent-hub-components/iceberg-iceberg-kafka-connect/lib

RUN set -eux; \
    curl -fsSL -o hadoop-common-3.3.4.jar "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.4/hadoop-common-3.3.4.jar" && \
    curl -fsSL -o hadoop-auth-3.3.4.jar "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-auth/3.3.4/hadoop-auth-3.3.4.jar" && \
    curl -fsSL -o hadoop-aws-3.3.4.jar "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar" && \
    curl -fsSL -o hadoop-hdfs-client-3.3.4.jar "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-hdfs-client/3.3.4/hadoop-hdfs-client-3.3.4.jar" && \
    curl -fsSL -o aws-java-sdk-bundle-1.12.262.jar "https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar" && \
    curl -fsSL -o commons-configuration2-2.8.0.jar "https://repo1.maven.org/maven2/org/apache/commons/commons-configuration2/2.8.0/commons-configuration2-2.8.0.jar" && \
    curl -fsSL -o commons-beanutils-1.9.4.jar "https://repo1.maven.org/maven2/commons-beanutils/commons-beanutils/1.9.4/commons-beanutils-1.9.4.jar" && \
    curl -fsSL -o commons-logging-1.2.jar "https://repo1.maven.org/maven2/commons-logging/commons-logging/1.2/commons-logging-1.2.jar" && \
    curl -fsSL -o commons-collections-3.2.2.jar "https://repo1.maven.org/maven2/commons-collections/commons-collections/3.2.2/commons-collections-3.2.2.jar" && \
    curl -fsSL -o commons-lang3-3.12.0.jar "https://repo1.maven.org/maven2/org/apache/commons/commons-lang3/3.12.0/commons-lang3-3.12.0.jar" && \
    curl -fsSL -o commons-text-1.10.0.jar "https://repo1.maven.org/maven2/org/apache/commons/commons-text/1.10.0/commons-text-1.10.0.jar" && \
    curl -fsSL -o guava-31.1-jre.jar "https://repo1.maven.org/maven2/com/google/guava/guava/31.1-jre/guava-31.1-jre.jar" && \
    curl -fsSL -o woodstox-core-6.4.0.jar "https://repo1.maven.org/maven2/com/fasterxml/woodstox/woodstox-core/6.4.0/woodstox-core-6.4.0.jar" && \
    curl -fsSL -o stax2-api-4.2.1.jar "https://repo1.maven.org/maven2/org/codehaus/woodstox/stax2-api/4.2.1/stax2-api-4.2.1.jar" && \
    curl -fsSL -o httpclient-4.5.13.jar "https://repo1.maven.org/maven2/org/apache/httpcomponents/httpclient/4.5.13/httpclient-4.5.13.jar" && \
    curl -fsSL -o httpcore-4.4.15.jar "https://repo1.maven.org/maven2/org/apache/httpcomponents/httpcore/4.4.15/httpcore-4.4.15.jar" && \
    curl -fsSL -o wildfly-openssl-1.0.7.Final.jar "https://repo1.maven.org/maven2/org/wildfly/openssl/wildfly-openssl/1.0.7.Final/wildfly-openssl-1.0.7.Final.jar"

# ensure plugin path permissions
RUN chown -R 1000:1000 /usr/share/confluent-hub-components

ENTRYPOINT ["/etc/confluent/docker/run"]
