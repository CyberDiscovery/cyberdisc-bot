#!/bin/bash

# Build and deploy only on master
if [ $BUILD_SOURCEBRANCHNAME == 'master' ] && [ $SYSTEM_PULLREQUEST_PULLREQUESTID == '' ]; then
    openssl aes-256-cbc -K $encrypted_6c901f41f0ce_key -iv $encrypted_6c901f41f0ce_iv -in id_rsa.enc -out id_rsa -d

    echo "Building image..."
    docker build -t cyberdiscovery/cdbot:latest .

    echo "Connecting to docker hub..."
    docker login -u "$DOCKER_USER" -p "$DOCKER_PASS"

    echo "Pushing image..."
    docker push cyberdiscovery/cdbot:latest

    echo "Deploying..."
    chmod 400 id_rsa
    ssh deploy@$DEPLOY_HOST -n -o "StrictHostKeyChecking=no" -i id_rsa
fi
