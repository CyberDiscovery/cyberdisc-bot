#!/bin/bash

# Build and deploy only on master
if [ $TRAVIS_BRANCH == 'master' ] && [ $TRAVIS_PULL_REQUEST == 'false' ]; then
    echo "Building image..."
    docker build -t cyberdiscovery/cyberdisc-bot:latest .

    echo "Connecting to docker hub..."
    docker login -u "$DOCKER_USER" -p "$DOCKER_PASS"

    echo "Pushing image..."
    docker push cyberdiscovery/cyberdisc-bot:latest

    echo "Deploying..."
    chmod 400 id_rsa
    ssh deploy@$DEPLOY_HOST -n -o "StrictHostKeyChecking=no" -i id_rsa
fi
