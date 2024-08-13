FROM node:slim
WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y \
        wget \
        gnupg \
        libgconf-2-4 \
        libnss3 \
        libxss1 \
        libgdk-pixbuf2.0-0 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcups2 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxtst6 \
        libnss3-tools \
        libdrm2 \
        libgbm1 \
        libasound2 \
        libatspi2.0-0 \
        libxrandr2 \
        libxfixes3 \
        libxkbcommon0 \
        libpango-1.0-0 \
        libcairo2

RUN npm install

RUN npx puppeteer browsers install chrome 

CMD node index.js