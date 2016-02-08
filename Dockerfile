FROM python:2.7
ADD . /code
RUN curl -fsSL https://get.docker.com/ | sh
RUN curl -fSSL https://get.docker.com/builds/Linux/x86_64/docker-1.9.1.tgz | tar -xzvf - 
RUN apt-get update
RUN apt-get install --yes redis-server
RUN pip install --upgrade pip
WORKDIR /code
RUN pip install -r requirements.txt
ENV C_FORCE_ROOT true
RUN curl --insecure -L https://download.getcarina.com/carina/latest/$(uname -s)/$(uname -m)/carina -o carina
RUN mv carina /usr/local/bin/carina
RUN chmod u+x /usr/local/bin/carina
CMD bash -c '$(eval carina env cutflow-compare) && honcho start' 