FROM postgres:15

WORKDIR /var/lib/postgresql/data

ENV TERM=xterm

RUN apt-get update
RUN apt-get install -y nano openssh-server sed

# Create SSH directory and set up SSH key for user
RUN mkdir /var/run/sshd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN ssh-keygen -A

# Create user for replication
COPY ./init-db.sh /docker-entrypoint-initdb.d/

CMD [ "postgres" ]