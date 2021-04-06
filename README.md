# cli

The [Astrobase](https://github.com/astrobase/astrobase) CLI Client

[![license](https://img.shields.io/badge/astrobase-license-blue.svg)](https://github.com/astrobase/cli/blob/master/LICENSE)
[![package](https://img.shields.io/github/v/release/astrobase/cli?sort=semver)](https://github.com/astrobase/cli/releases)
[![publish](https://github.com/astrobase/cli/actions/workflows/publish.yaml/badge.svg)](https://github.com/astrobase/cli/actions/workflows/publish.yaml)
[![test](https://github.com/astrobase/cli/actions/workflows/test.yaml/badge.svg?branch=master)](https://github.com/astrobase/cli/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/astrobase/cli/branch/master/graph/badge.svg?token=97YCqzHZmk)](https://codecov.io/gh/astrobase/cli)

The Astrobase CLI is the best way to issue commands to the Astrobase API server to initialize the server, create clusters, resources, and manage Astrobase profiles.

## Requirements

The CLI requires that a few commands are available in your path.

- python3.9+ (we suggest installing with [pyenv](https://github.com/pyenv/pyenv))
- [docker](https://docs.docker.com/get-docker/)
- [aws-cli](https://github.com/aws/aws-cli#installation)
- [gcloud](https://cloud.google.com/sdk/docs/install#installation_instructions)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (if you've already installed gcloud, kubectl will already be available)

## Installation

Install via `pip`

```sh
python -m pip install astrobase_cli
```

Check that the installation worked

```sh
astrobase
```

## Features and Usage

### Checks

Checks help you make sure that everything is ready to roll in your environment.

Run `astrobase check commands` to make sure that the necessary commands are in your `$PATH` to use Astrobase.

### Profiles

Astrobase profiles are json objects that live in `~/.astrobase/config.json` by default. A `config.json` looks like:

```json
{
  "my-profile": {
    "name": "my-profile",
    "server": "http://localhost:8787",
    "gcp_creds": "/absolute/path/to/my/credentials.json",
    "aws_creds": "/absolute/path/to/my/.aws/credentials",
    "aws_profile_name": "default"
  }
}
```

You can view commands to interact with Astrobase profiles by running `astrobase profile --help`.

Let's walk through and example of setting up an Astrobase profile.

First, let's create a profile:

```sh
$ astrobase profile create my-profile \
--gcp-creds /absolute/path/to/my/credentials.json \
--aws-creds /absolute/path/to/my/.aws/credentials \
--aws-profile-name default
Created profile my-profile.
```

Next, check that it exists.

```sh
$ astrobase profile get
{
  "my-profile": {
    "name": "my-profile",
    "server": "http://localhost:8787",
    "gcp_creds": "/absolute/path/to/my/credentials.json",
    "aws_creds": "/absolute/path/to/my/.aws/credentials",
    "aws_profile_name": "default"
  }
}
```

Now let's set it to be our current profile ... how do we do that?

```sh
$ astrobase profile current
ASTROBASE_PROFILE environment variable is not set properly.
Please set it with `export ASTROBASE_PROFILE=<your-profile-name>`
View profile names with `astrobase profile get | jq 'keys'`
```

Ah – nice.

```sh
$ export ASTROBASE_PROFILE=my-profile
$ astrobase profile current
{
  "name": "my-profile",
  "server": "http://localhost:8787",
  "gcp_creds": "/absolute/path/to/my/credentials.json",
  "aws_creds": "/absolute/path/to/my/.aws/credentials",
  "aws_profile_name": "default"
}
```

Awesome. Now we're ready to initialize Astrobase and deploy clusters and resources.

### Initializing Astrobase

Once you've set your current profile you can initialize Astrobase. You will have to specify a couple of environment variables to make sure you can connect to cloud providers.

```sh
$ astrobase init
Initializing Astrobase ...
Starting Astrobase server ...
Astrobase initialized and running at http://localhost:8787
```

Sweet. Now we can check that Astrobase was kicked off locally.

```sh
$ docker ps -a
CONTAINER ID   IMAGE                                 COMMAND                  CREATED         STATUS         PORTS                    NAMES
da589f68847e   gcr.io/astrobaseco/astrobase:latest   "/bin/sh -c 'gunicor…"   7 seconds ago   Up 6 seconds   0.0.0.0:8787->8787/tcp   astrobase-my-profile
```

The Astrobase API server is built on top of [FastAPI](https://github.com/tiangolo/fastapi), which is incredibly awesome.

To check that everything's healthy, curl to the healthcheck endpoint or visit http://localhost:8787/docs to interact with the api server's swagger.

```sh
$ curl -s "http://:8787/healthcheck" | jq
{
  "message": "We're on the air.",
  "time": "2021-04-06 18:29:15.276198",
  "apiVersion": "0.1.0"
}
```

### Preliminary Setup for AWS Deployments

In order to deploy clusters on AWS (EKS), you'll need to do some preliminary setup.

The Astrobase API will handle infrastructure provisioning, but you will need to pull together a few resource identifiers.

Here's an [example yaml cluster definition for an EKS Cluster](tests/assets/test-eks-cluster.yaml).

There are a few values in there that we have to specify on the command line to pass into this cluster definition, namely ...

```
$SUBNET_ID_0
$SUBNET_ID_1
$SECURITY_GROUP
$CLUSTER_ROLE_ARN
$NODE_ROLE_ARN
```

To deploy the cluster into your default VPC use the following. For your own VPCs you'll need to specify those yourself. Note that these variables can be named whatever you like and aren't tied to a schema.

```sh
export SUBNET_ID_0=$(aws ec2 describe-subnets --query 'Subnets[].SubnetId[]' | jq -r '.[0]')
export SUBNET_ID_1=$(aws ec2 describe-subnets --query 'Subnets[].SubnetId[]' | jq -r '.[1]')
export SECURITY_GROUP=$(aws ec2 describe-security-groups --query 'SecurityGroups[].GroupId' | jq -r '.[0]')
```

Now for the ARNs. You'll need an ARN for the cluster and another for each nodegroup you want to create.

#### CLUSTER_ROLE_ARN

1. Create an IAM role, call it whatever you like. For documentation's sake, we'll call it `AstrobaseEKSRole`.
1. Attach the AWS managed policy, titled `AmazonEKSClusterPolicy`.
1. Set it in your environment: `export CLUSTER_ROLE_ARN=arn:aws:iam::account_id:role/AstrobaseEKSRole`

#### NODE_ROLE_ARN

1. Create an IAM role, call it whatever you like. For documentation's sake, we'll call it `AstrobaseEKSNodegroupRole`.
1. Attach the following AWS managed policies, titled: `AmazonEKSWorkerNodePolicy`, `AmazonEC2ContainerRegistryReadOnly`, `AmazonEKS_CNI_Policy`
1. Set it in your environment: `export NODE_ROLE_ARN=arn:aws:iam::account_id:role/AstrobaseEKSNodegroupRole`

#### AWS Configure

Make sure you can complete the `aws configure` login flow.

### Preliminary Setup for GCP Deployments

In order to deploy clusters on GCP (GKE), you'll need to do some preliminary setup.

#### Project ID and Google Application Credentials

You'll need to have a Google Cloud project created already with the GKE (Google Kubernetes Engine) and GCE (Google Compute Engine) APIs enabled.

```sh
export PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT_EMAIL=$(gcloud iam service-accounts list --filter="display_name:Default compute service account" --format=json | jq -r ".[].email")
gcloud iam service-accounts keys create ~/astrobase-gcp-creds.json --iam-account $SERVICE_ACCOUNT_EMAIL
```

Make sure you can complete the `gcloud auth login` flow from the shell session from which you're using Astrobase to deploy clusters and resources. You can use `astrobase commands check` to make sure all the commands you need are accessible.

### Apply and Destroy


