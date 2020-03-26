#!/bin/bash

# export POLYAXON_NO_OP=1

#app_name=$(git branch | grep \* | cut -d ' ' -f2)
app_name=$CI_COMMIT_REF_NAME


# next_assignment=$(find . -maxdepth 1 -name "assignment*" | wc -l | tr -d '[:space:]')

# current=$(($next_assignment - 1))

# echo "Current assignment: $current"

# current_assignment="assignment$current"

# echo "Evaluating $current_assignment"

# post_evaluation() {

#     curl -X POST \
#       "$WEB_HOOK_URL" \
#       -H "Content-Type: application/json; charset=UTF-8" \
#       -d '{ "text": "'"$post_text"'",
#            "thread": { "name": "spaces/'"${CHATROOM_ID}"'/threads/'"${!current_assignment}"'" }
#       }'

# }

# echo "export PATH="~/anaconda3/bin:$PATH"" >> ~/.bashrc
# source ~/.bashrc

cat /proc/version
echo "Updating apt-get"
apt-get update

echo "Updating libc6"
apt-cache policy libc6
apt-get install libc6
apt-get -y install --reinstall build-essential
apt-get install -y python-sqlalchemy
# aptitude reinstall gcc-5 g++-5


apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EB3E94ADBE1229CF
apt-get install apt-transport-https ca-certificates
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add
curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

echo "Updating apt-get"
apt-get update
ACCEPT_EULA=Y apt-get -y install msodbcsql17
apt-get -y install unixodbc unixodbc-dev


if [ -d "./tests" ]
then
    if [ ! -f "./requirements.txt" ]
    then
        echo "No requirements.txt file found"
        exit 1
    fi

    # conda env update -n base --file "./environment.yml"
    pip install --upgrade pip
    pip install -r "./requirements.txt"
    # Manually put these back since conda env update removes them
    pip install pytest pylint radon

    pytest -x "./tests"

    if [ "$?" -gt "0" ]
    then
        echo "Test failed"
        exit 1
    fi

else
    echo "No tests. Skipping eval and posting to chat channel."
    post_text="No tests. Skipping eval for $app_name"
    # post_evaluation
fi
