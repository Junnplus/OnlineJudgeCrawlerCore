FROM python:2.7

EXPOSE 6800
ADD . /opt/ojcc
WORKDIR /opt/ojcc
RUN pip install -r requirements.txt

ADD scrapyd.conf /etc/scrapyd/scrapyd.conf
ADD supervisord.conf /etc/supervisord.conf
ADD supervisord /etc/init.d/supervisord
CMD supervisord -c /etc/supervisord.conf
