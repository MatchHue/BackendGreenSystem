#Grab the latest alpine image
#FROM minizinc/minizinc:latest-alpine
FROM minizinc/minizinc:latest

# Install python and pip
#RUN apk add --no-cache --update python3 py3-pip bash
#RUN apt-get add --no-cache --update python3 py3-pip bash

RUN apt-get update
RUN apt-get -y install python3-pip

ADD ./requirements.txt /tmp/requirements.txt

RUN pip3 install --upgrade pip setuptools wheel

#RUN pip3 install scipy
# Install dependencies
RUN pip3 install -r /tmp/requirements.txt

# Add our code
ADD . /opt/webapp/
WORKDIR /opt/webapp

# Expose is NOT supported by Heroku
# EXPOSE 5000 		

# Run the image as a non-root user
#RUN adduser -D myuser
#USER myuser

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku			
#CMD gunicorn --bind 0.0.0.0:$PORT wsgi 
CMD python3 main.py