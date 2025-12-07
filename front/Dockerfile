FROM node:22
WORKDIR /app

COPY . .
RUN node i --silent
RUN node run build

EXPOSE 8080

CMD node run start