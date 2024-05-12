FROM centos:latest

RUN cd /etc/yum.repos.d/
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

#RUN yum update
RUN yum install python39 -y
RUN curl -sSL https://install.python-poetry.org | python3 -

CMD ["tail", "-f", "/dev/null"]
