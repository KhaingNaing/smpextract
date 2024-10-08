# base image 
FROM python:3-alpine 

# Set working dir 
WORKDIR /zone 

RUN apk add --no-cache git && \
    pip install git+https://github.com/KhaingNaing/smpextract.git#egg=smpextract && \
    pip install pandas && \
    apk del git 

ENTRYPOINT [ "smpextract" ]


