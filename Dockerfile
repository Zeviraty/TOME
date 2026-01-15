FROM python:3
RUN apt-get update && apt-get install -y make
COPY src/ src/
COPY db/schemas db/schemas
COPY .gitignore .gitignore
COPY .gitattributes .gitattributes
COPY configure configure
COPY makefile makefile
COPY README.md README.md
COPY requirements.txt requirements.txt
COPY pyproject.toml pyproject.toml
COPY config/ config/
RUN chmod +x configure
RUN ./configure
RUN make install DOCKER=1 && make clean
EXPOSE 2323
CMD ["make","run"]
