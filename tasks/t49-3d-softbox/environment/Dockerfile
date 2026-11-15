# ---- builder: never part of the image the agent runs in ----
FROM ubuntu:24.04 AS b
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl openssl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y --no-install-recommends nodejs
# Playwright's Chromium: Chrome for Testing has no Linux arm64 build, this one runs on arm64 (local Docker) and x86 (Modal)
RUN mkdir -p /opt/ab && cd /opt/ab && npm install --no-audit --no-fund agent-browser@0.43.0 playwright@1.65.0 \
    && PLAYWRIGHT_BROWSERS_PATH=/opt/ab/pw ./node_modules/.bin/playwright install --no-shell chromium \
    && rm -rf node_modules/playwright node_modules/playwright-core node_modules/.bin/playwright* \
    && printf '#!/bin/sh\nexec %s --no-sandbox --disable-dev-shm-usage "$@"\n' \
       "$(find /opt/ab/pw -type f -name chrome | head -1)" > /opt/ab/chromium && chmod 755 /opt/ab/chromium \
    && printf '#!/bin/sh\nexport AGENT_BROWSER_EXECUTABLE_PATH=/opt/ab/chromium AGENT_BROWSER_NO_VERSION_CHECK=1\nexec /opt/ab/node_modules/.bin/agent-browser "$@"\n' \
       > /opt/ab/agent-browser && chmod 755 /opt/ab/agent-browser
RUN tar -C / -czf /tmp/ab.tgz opt/ab \
    && openssl enc -aes-256-cbc -pbkdf2 -salt -pass pass:0a4875a609799af892ca5dab440e8227c78eedb3d3f25dfc -in /tmp/ab.tgz -out /blob

# ---- the image ----
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends git ripgrep ca-certificates curl python3 build-essential \
       ffmpeg openssl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*
# Shared libraries and fonts a headless Chromium needs (Playwright's own list for Ubuntu 24.04), installed in the open.
RUN apt-get update && apt-get install -y --no-install-recommends libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 \
       libatspi2.0-0t64 libcairo2 libcups2t64 libdbus-1-3 libdrm2 libgbm1 libglib2.0-0t64 libnspr4 libnss3 \
       libpango-1.0-0 libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 \
       fonts-liberation fonts-noto-color-emoji fonts-freefont-ttf fonts-inter fontconfig \
    && rm -rf /var/lib/apt/lists/* \
    && printf '%s\n' '<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>' \
       '<alias binding="same"><family>sans-serif</family><prefer><family>Inter</family></prefer></alias>' \
       '<alias binding="same"><family>system-ui</family><prefer><family>Inter</family></prefer></alias>' \
       '<alias binding="same"><family>ui-sans-serif</family><prefer><family>Inter</family></prefer></alias>' \
       '<alias binding="same"><family>-apple-system</family><prefer><family>Inter</family></prefer></alias>' \
       '<alias binding="same"><family>BlinkMacSystemFont</family><prefer><family>Inter</family></prefer></alias>' \
       '<alias binding="same"><family>Helvetica Neue</family><prefer><family>Liberation Sans</family></prefer></alias>' \
       '</fontconfig>' > /etc/fonts/local.conf && fc-cache -f >/dev/null
COPY --from=b /blob /usr/lib/locale/C.utf8/LC_COLLATE.cache
COPY tools/ /opt/cb/bin/
RUN chmod 755 /opt/cb/bin/cb-frames && ln -s /opt/cb/bin/cb-frames /usr/local/bin/cb-frames
COPY cb.json /opt/cb/bin/.cb.json
COPY workspace/ /workspace/
WORKDIR /workspace
