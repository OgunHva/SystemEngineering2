FROM debian

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  vim \
  sudo \
  default-jdk \
  openssh-server \
  wget

#RUN useradd -ms /bin/bash hadoop

RUN useradd -m hadoop && echo "hadoop:hadoop" | chpasswd && adduser hadoop sudo
USER hadoop
WORKDIR /home/hadoop

RUN wget http://ftp.tudelft.nl/apache/hadoop/common/hadoop-3.1.2/hadoop-3.1.2.tar.gz
RUN tar -xzf hadoop-3.1.2.tar.gz
RUN cp -r hadoop-3.1.2 hadoop
RUN rm -r hadoop-3.1.2

CMD /bin/bash
