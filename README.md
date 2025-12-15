<div align="center">
  <br>
  <h1>Tome MUD</h1>
  <strong>For creating 🌟Amazing🌟 MUD/MUX/MUSH/MU* </strong>
  <br><br>
  <a href="https://python.org">
    <img src="https://forthebadge.com/images/badges/made-with-python.svg" alt="Made with Python">
  </a>
  <a href="https://forthebadge.com">
    <img src="https://forthebadge.com/images/badges/open-source.svg" alt="Open Source">
  </a>
  <a href="https://forthebadge.com">
    <img src="https://forthebadge.com/images/badges/built-with-love.svg" alt="Built with love">
  </a>
</div>

<p align="center">
  <a href="https://choosealicense.com/licenses/gpl-3.0/">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="GPLv3 License">
  </a>
</p>

# About TOME

> [!WARNING] This project is unfinished and in alpha, come help out!

TOME is a multi-user text engine designed to be used with traditional mud clients.
This is the successor to my mud engine ARMUD

# Installation
## From source / git
1. Clone the repository `git clone git@github.com:zeviraty/TOME` or `git clone https://github.com/zeviraty/TOME`
2. Run configure script: `./configure`
3. Run install: `make install`
4. Run code check: `make check`
5. You are good to go!

## Docker
### From docker hub
1. Pull the docker image `docker pull zevvi/tome:latest` or `docker pull zevvi/tome:nightly` for nightly
2. Run the docker image `docker run zevvi/tome:latest` or `docker run zevvi/tome:nightly`
### From source
1. Clone the repository `git clone git@github.com:zeviraty/TOME` or `git clone https://github.com/zeviraty/TOME`
2. Build the docker image `docker build . -t tome:nightly`
3. Run the docker image `docker run tome:nightly`

# Modular
Everything is in configuration files under the config/ directory:
 - Classes
 - Races
 - Profanity
 - Commands

## License

This project is licensed under the GNU General Public License v3.0 License.
Full license: [GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
