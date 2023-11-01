﻿# Affective Input Framework

Docker and PM2 is required to run this project.

PM2 Installation Guide:
https://pm2.keymetrics.io/docs/usage/quick-start/

Docker Installation Guide:
https://www.docker.com/products/docker-desktop/

#### How to Run:

1. Pull and run docker image first, by running docker-compose up.
2. Run this command to start the services (might need to wait a bit for all the services to start):

   ```
   pm2 start ./ecosystem.config.js
   ```
3. To demo, run this command:

   ```
   python ./input_service/main.py && pm2 logs
   ```

#### References:

1. https://huggingface.co/SamLowe/roberta-base-go_emotions
