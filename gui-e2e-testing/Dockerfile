FROM mcr.microsoft.com/playwright:v1.17.1
WORKDIR /e2e
ENV CI=1
RUN curl -SL --fail "https://mender.s3-accelerate.amazonaws.com/temp_master/core-image-full-cmdline-qemux86-64.ext4" \
  -o core-image-full-cmdline-qemux86-64.ext4 && \
  curl -SL --fail -P fixtures "https://dgsbl4vditpls.cloudfront.net/mender-demo-artifact.mender" \
  -o mender-demo-artifact.mender && \
  curl -SL --fail "https://d1b0l86ne08fsf.cloudfront.net/mender-artifact/master/mender-artifact" \
  -o /usr/bin/mender-artifact && \
  chmod +x /usr/bin/mender-artifact
ADD https://raw.githubusercontent.com/mendersoftware/gui/master/tests/e2e_tests/package.json ./
ADD https://raw.githubusercontent.com/mendersoftware/gui/master/tests/e2e_tests/package-lock.json ./
RUN npm ci && npx playwright install
