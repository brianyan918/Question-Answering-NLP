# Ubuntu Linux as the base imag
FROM ubuntu:18.04

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install packages
RUN apt-get -y update && \
    apt-get -y upgrade && \
	apt-get -y install python3-pip python3-dev

RUN pip3 install spacy==2.1.0 && \
    pip3 install textacy==0.8.0 && \
    python3 -m spacy download en_core_web_sm

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

RUN git clone https://github.com/huggingface/neuralcoref.git &&\
    cd neuralcoref &&\
    pip3 install -r requirements.txt &&\
    pip3 install -e . &&\
    cd ..

# Add the files
RUN mkdir /QA
ADD ask /QA
ADD answer /QA
ADD open_questions.py /QA
ADD answer_generator.py /QA
ADD setup.py /QA

RUN mkdir /host && \
    cd host && \
    mkdir Users && \
    cd Users && \
    mkdir data

ADD test_questions.txt /host/Users
ADD data/*.txt /host/Users/data/

CMD ["chmod 777 ask"]
CMD ["chmod 777 answer"]
CMD ["chmod 777 open_questions.py"]
CMD ["chmod 777 answer_generator.py"]
CMD ["chmod 777 a1.txt"]
CMD ["chmod 777 test_questions.txt"]

# Set working dir as /QA
WORKDIR /QA
ENTRYPOINT ["/bin/bash" , "-c"]

RUN python3 setup.py