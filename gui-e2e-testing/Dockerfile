FROM mcr.microsoft.com/playwright:v1.19.2
WORKDIR /e2e
ENV CI=1
RUN curl -SL --fail -P fixtures "https://dgsbl4vditpls.cloudfront.net/mender-demo-artifact.mender" \
  -o mender-demo-artifact.mender
ADD https://raw.githubusercontent.com/mendersoftware/gui/master/tests/e2e_tests/package.json ./
ADD https://raw.githubusercontent.com/mendersoftware/gui/master/tests/e2e_tests/package-lock.json ./
RUN npm ci && npx playwright install
