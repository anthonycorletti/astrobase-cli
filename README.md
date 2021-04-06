# astrobase_cli

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
$ python -m pip install astrobase_cli
```

Check that the installation worked

```sh
$ astrobase
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

### Apply and Destroy Clusters and Kubernetes Resources

#### Google Kubernetes Engine

Deploying clusters and resources with Astrobase is incredibly easy.

Let's deploy a cluster on GCP first, and then deploy the kubernetes dashboard and an nginx server to the cluster.

First, let's take a look at the apply command `astrobase apply --help`

```sh
$ astrobase apply --help
Usage: astrobase apply [OPTIONS]

  Apply clusters and resources.

Options:
  -f TEXT  [required]
  -v TEXT  Parameters to pass into your yaml. Format:
           key=value<space>key2=value2<space>key3=value3<space>...

  --help   Show this message and exit.
```

Yup – that's all you need, specify the cluster resource file with `-f` like kubernetes file references, and `-v` to pass parameters in the format of space separated key-value pairs.

Let's give it a go. We can use the test asset files for a quick example.

```sh
$ astrobase apply -f tests/assets/test-gke-cluster.yaml -v PROJECT_ID=my-project-id
{
  "name": "operation-1617740520664-1720b4ce",
  "zone": "us-central1",
  "operationType": "CREATE_CLUSTER",
  "status": "RUNNING",
  "selfLink": "https://container.googleapis.com/v1beta1/projects/PROJECT_NUMBER/locations/us-central1/operations/operation-1617740520664-1720b4ce",
  "targetLink": "https://container.googleapis.com/v1beta1/projects/PROJECT_NUMBER/locations/us-central1/clusters/astrobase-test-gke",
  "startTime": "2021-04-06T20:22:00.664820492Z"
}
```

It takes some time for the cluster to create – so give it five minutes or so. You can check the status of the cluster via the astrobase-api. This command will only work properly if you have one cluster in your project. Best to do this in a test project so you dont heck up things.

```sh
$ curl -s -X GET "http://:8787/gke?project_id=my-project-id&location=us-central1" | jq '.clusters[0].status'
"PROVISIONING"
...
$ curl -s -X GET "http://:8787/gke?project_id=my-project-id&location=us-central1" | jq '.clusters[0].status'
"RUNNING" 🙌
```

Awesome – now deploy your resources.

```sh
$ astrobase apply -f tests/assets/test-resources-gke.yaml
applying resources to astrobase-test-gke@us-central1
namespace/kubernetes-dashboard created
serviceaccount/kubernetes-dashboard created
service/kubernetes-dashboard created
secret/kubernetes-dashboard-certs created
secret/kubernetes-dashboard-csrf created
secret/kubernetes-dashboard-key-holder created
configmap/kubernetes-dashboard-settings created
role.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrole.rbac.authorization.k8s.io/kubernetes-dashboard created
rolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
deployment.apps/kubernetes-dashboard created
service/dashboard-metrics-scraper created
deployment.apps/dashboard-metrics-scraper created
applying resources to astrobase-test-gke@us-central1
deployment.apps/nginx-deployment created
```

Run `kubectl proxy` to checkout the kubernetes dashboard at

```
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

You'll have to specify a kubeconfig reference, luckily, astrobase just uses `~/.kube/config` – so just use that!

Easy right? Let's follow through a similar exercise on AWS EKS next.

#### Elastic Kubernetes Engine

Remember setting a bunch of values before for subnets, ARNs, and such? Now here's where Astrobase's simple templating really shines.

```sh
$ export CLUSTER_ROLE_ARN=arn:aws:iam::AWS_ACCOUNT_ID:role/AstrobaseEKSRole
$ export NODE_ROLE_ARN=arn:aws:iam::AWS_ACCOUNT_ID:role/AstrobaseEKSNodegroupRole
$ export SUBNET_ID_0=$(aws ec2 describe-subnets --query 'Subnets[].SubnetId[]' | jq -r '.[0]')
$ export SUBNET_ID_1=$(aws ec2 describe-subnets --query 'Subnets[].SubnetId[]' | jq -r '.[1]')
$ export SECURITY_GROUP=$(aws ec2 describe-security-groups --query 'SecurityGroups[].GroupId' | jq -r '.[0]')

$ astrobase apply -f tests/assets/test-eks-cluster.yaml -v "CLUSTER_ROLE_ARN=$CLUSTER_ROLE_ARN NODE_ROLE_ARN=$NODE_ROLE_ARN SUBNET_ID_0=$SUBNET_ID_0 SUBNET_ID_1=$SUBNET_ID_1 SECURITY_GROUP=$SECURITY_GROUP"
{
  "message": "EKS create request submitted for astrobase-test-eks"
}
```

EKS behaves differently and some async api calls need to be handled to provision nodegroups, that's the api server's job.

So we can hangout for a little while that cluster provisions.

```sh
$ curl -s -X GET "http://:8787/eks/astrobase-test-eks?region=us-east-1" | jq '.cluster.status'
"CREATING"
```

Once this is ready, we can check that nodegroups are getting set up. If something goes wrong we can always check the container's logs

```sh
$ docker logs astrobase-$MY_PROFILE_NAME
```

And just like deploying resources to GKE, do the same for EKS.


```sh
$ astrobase apply -f tests/assets/test-resources-eks.yaml
applying resources to astrobase-test-eks@us-east-1
namespace/kubernetes-dashboard created
serviceaccount/kubernetes-dashboard created
service/kubernetes-dashboard created
secret/kubernetes-dashboard-certs created
secret/kubernetes-dashboard-csrf created
secret/kubernetes-dashboard-key-holder created
configmap/kubernetes-dashboard-settings created
role.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrole.rbac.authorization.k8s.io/kubernetes-dashboard created
rolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
deployment.apps/kubernetes-dashboard created
service/dashboard-metrics-scraper created
deployment.apps/dashboard-metrics-scraper created
applying resources to astrobase-test-eks@us-east-1
deployment.apps/nginx-deployment created
```
