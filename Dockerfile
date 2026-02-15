FROM python:3
RUN apt-get update && apt-get install -y make
COPY src/ src/
COPY configure configure
COPY makefile makefile
COPY requirements.txt requirements.txt
COPY pyproject.toml pyproject.toml
COPY defaults/ defaults/
COPY schemas/ schemas/
RUN chmod +x configure
RUN ./configure
RUN make install DOCKER=1 && make clean
EXPOSE 2323
CMD ["make","run"]
