# base image 
FROM python:3-alpine 

# Set working dir 
WORKDIR /zone 

RUN apk add --no-cache git && \
    pip install git+https://github.com/KhaingNaing/cpbyext.git#egg=cpbyext && \
    pip install pandas && \
    apk del git 

ENTRYPOINT["smpextract"]


