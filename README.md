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
  <a href="https://choosealicense.com/licenses/gpl-3.0">
    <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxOTQuMjgxMzQxNTUyNzM0MzgiIGhlaWdodD0iMzUiIHZpZXdCb3g9IjAgMCAxOTQuMjgxMzQxNTUyNzM0MzggMzUiPjxyZWN0IHdpZHRoPSI4NS4zMTI1MzgxNDY5NzI2NiIgaGVpZ2h0PSIzNSIgZmlsbD0iIzMxQzRGMyIvPjxyZWN0IHg9Ijg1LjMxMjUzODE0Njk3MjY2IiB3aWR0aD0iMTA4Ljk2ODgwMzQwNTc2MTcyIiBoZWlnaHQ9IjM1IiBmaWxsPSIjMzg5QUQ1Ii8+PHRleHQgeD0iNDIuNjU2MjY5MDczNDg2MzMiIHk9IjIxLjUiIGZvbnQtc2l6ZT0iMTIiIGZvbnQtZmFtaWx5PSInUm9ib3RvJywgc2Fucy1zZXJpZiIgZmlsbD0iI0ZGRkZGRiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgbGV0dGVyLXNwYWNpbmc9IjIiPkxJQ0VOU0U8L3RleHQ+PHRleHQgeD0iMTM5Ljc5NjkzOTg0OTg1MzUyIiB5PSIyMS41IiBmb250LXNpemU9IjEyIiBmb250LWZhbWlseT0iJ01vbnRzZXJyYXQnLCBzYW5zLXNlcmlmIiBmaWxsPSIjRkZGRkZGIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXdlaWdodD0iOTAwIiBsZXR0ZXItc3BhY2luZz0iMiI+R05VIEdQTFYzPC90ZXh0Pjwvc3ZnPg==" alt="GNU GPLV3 LICENSE">
  </a>
</div>

# About TOME

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
