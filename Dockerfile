FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 make python3-pip
COPY src/ src/
COPY db/schemas db/schemas
COPY .gitignore .gitignore
COPY .gitattributes .gitattributes
COPY configure configure
COPY makefile makefile
COPY README.md README.md
COPY requirements.txt requirements.txt
RUN chmod +x configure
RUN ./configure
RUN make install && make clean
EXPOSE 2323
CMD ["make","run"]
