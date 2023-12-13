# pull official base image
FROM node:16-alpine

# set working directory
WORKDIR /app

COPY package.json /app
COPY package-lock.json /app

RUN npm install --legacy-peer-deps

# add app
COPY . /app
EXPOSE 5000

# start app
CMD ["npm", "start"]

