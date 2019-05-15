FROM debian

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  vim \
  sudo \
  default-jdk \
  openssh-server \
  wget

ARG SSH_PRIVATE_KEY
ARG SSH_PUBLIC_KEY
RUN mkdir /var/run/sshd

RUN useradd -m hadoop && echo "hadoop:hadoop" | chpasswd && adduser hadoop sudo
WORKDIR /home/hadoop
RUN mkdir /home/hadoop/.ssh
RUN echo "${SSH_PRIVATE_KEY}" > /home/hadoop/.ssh/id_rsa
RUN echo "${SSH_PUBLIC_KEY}" > /home/hadoop/.ssh/authorized_keys
RUN chmod -R 700 /home/hadoop/.ssh
RUN chown -R hadoop:hadoop /home/hadoop

RUN echo "hadoop ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo "root:hadoop" | chpasswd
RUN echo "PasswordAuthentication no" >> /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN echo "hadoop ALL=(ALL) NOPASSWD: ALL" | (EDITOR="tee -a" visudo)

#WORKDIR /home/hadoop
RUN wget http://ftp.tudelft.nl/apache/hadoop/common/hadoop-3.1.2/hadoop-3.1.2.tar.gz
RUN tar -xzf hadoop-3.1.2.tar.gz
RUN cp -r hadoop-3.1.2 hadoop
RUN rm -r hadoop-3.1.2
RUN mkdir /home/hadoop/hadoop/logs
RUN chown -R hadoop /home/hadoop/hadoop

CMD ["/usr/sbin/sshd", "-D"]
EXPOSE 22
