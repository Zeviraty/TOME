FROM python:3
RUN apt-get update && apt-get install -y make
ADD src/
ADD db/schemas
ADD .gitignore
ADD .gitattributes
ADD configure
ADD makefile
ADD README.md
ADD requirements.txt
ADD pyproject.toml
ADD defaults/
ADD schemas/
RUN chmod +x configure
RUN ./configure
RUN make install DOCKER=1 && make clean
EXPOSE 2323
CMD ["make","run"]
