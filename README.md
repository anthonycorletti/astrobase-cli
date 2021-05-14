# astrobase_cli

The [Astrobase](https://github.com/astrobase/astrobase) CLI Client

[![publish](https://github.com/astrobase/cli/actions/workflows/publish.yaml/badge.svg)](https://github.com/astrobase/cli/actions/workflows/publish.yaml)
[![test](https://github.com/astrobase/cli/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/astrobase/cli/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/astrobase/cli/branch/main/graph/badge.svg?token=97YCqzHZmk)](https://codecov.io/gh/astrobase/cli)

The Astrobase CLI is the best way to send requests to the Astrobase API server, create clusters and resources, and manage Astrobase profiles.

## Requirements

The CLI requires a few things to get started.

- python3.9+ (we suggest installing with [pyenv](https://github.com/pyenv/pyenv))
- [docker](https://docs.docker.com/get-docker/) should be available on your machine
- [kubectl](https://kubernetes.io/docs/tasks/tools/): a recent version (1.18+ should do!)

Credentials available for the following cloud accounts:

- Google Cloud: create [a service account credential](https://cloud.google.com/iam/docs/creating-managing-service-account-keys). This could be the same credential that you've set in `astrobase profile current`.
- AWS: Install and configur the [`aws-cli`](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html). Simply running `aws configure` and setting the correct credentials will do.
- Azure: [Values for your subscription ID, client ID, tenant ID, and client secret](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal). Simply export those values in your environment like so;
    ```
    export AZURE_TENANT_ID={your tenant id}
    export AZURE_CLIENT_ID={your client id}
    export AZURE_CLIENT_SECRET={your client secret}
    export AZURE_SUBSCRIPTION_ID={your subscription id}
    ```


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

Run `astrobase check commands` to make sure that the necessary commands are in your `$PATH` to use Astrobase. You want to make sure that a docker daemon is available and `kubectl` is in your path. These dependencies may be removed in the future with a rewrite in [go](https://golang.com).

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

First, let's create a profile. You will need to have credentials for each cloud provider you wish to use. You only need to configure the cloud providers you wish to use.

In order for Astrobase to work properly, we suggest that you use your default AWS credentials, and for GCP, create a new json key for your default compute service account.

Make sure you reference these files correctly, these are placeholders.

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
  "zone": "us-central1-c",
  "operationType": "CREATE_CLUSTER",
  "status": "RUNNING",
  "selfLink": "https://container.googleapis.com/v1beta1/projects/PROJECT_NUMBER/zones/us-central1-c/operations/operation-1617740520664-1720b4ce",
  "targetLink": "https://container.googleapis.com/v1beta1/projects/PROJECT_NUMBER/zones/us-central1-c/clusters/astrobase-test-gke",
  "startTime": "2021-04-06T20:22:00.664820492Z"
}
```

It takes some time for the cluster to create – so give it five minutes or so. You can check the status of the cluster via the astrobase-api. This command will only work properly if you have one cluster in your project. Best to do this in a test project so you dont heck up things.

```sh
$ curl -s -X GET "http://:8787/gke?project_id=my-project-id&location=us-central1-c" | jq '.clusters[0].status'
"PROVISIONING"
...
$ curl -s -X GET "http://:8787/gke?project_id=my-project-id&location=us-central1-c" | jq '.clusters[0].status'
"RUNNING" 🙌
```

Awesome – now deploy your resources.

```sh
$ astrobase apply -f tests/assets/test-resources-gke.yaml
applying resources to astrobase-test-gke@us-central1-c
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
applying resources to astrobase-test-gke@us-central1-c
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
...
$ curl -s -X GET "http://:8787/eks/astrobase-test-eks?region=us-east-1" | jq '.cluster.status'
"ACTIVE"
...
$ curl -s -X GET "http://:8787/eks/astrobase-test-eks/nodegroups/test-nodegroup-cpu?region=us-east-1" | jq '.nodegroup.status'
"CREATING"
...
$ curl -s -X GET "http://:8787/eks/astrobase-test-eks/nodegroups/test-nodegroup-cpu?region=us-east-1" | jq '.nodegroup.status'
"ACTIVE"
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

#### Destroying Clusters

Easy come, easy go!

```sh
$ astrobase destroy -f tests/assets/test-gke-cluster.yaml -v PROJECT_ID=$PROJECT_ID
{
  "name": "operation-1617745193119-31995a6b",
  "zone": "us-central1-c",
  "operationType": "DELETE_CLUSTER",
  "status": "RUNNING",
  "selfLink": "https://container.googleapis.com/v1beta1/projects/PROJECT_NUMBER/zones/us-central1-c/operations/operation-1617745193119-31995a6b",
  "targetLink": "https://container.googleapis.com/v1beta1/projects/PROJECT_NUMBER/zones/us-central1-c/clusters/astrobase-test-gke",
  "startTime": "2021-04-06T21:39:53.119493584Z"
}
$ astrobase destroy -f tests/assets/test-eks-cluster.yaml -v "CLUSTER_ROLE_ARN=$CLUSTER_ROLE_ARN NODE_ROLE_ARN=$NODE_ROLE_ARN SUBNET_ID_0=$SUBNET_ID_0 SUBNET_ID_1=$SUBNET_ID_1 SECURITY_GROUP=$SECURITY_GROUP"
{
  "message": "EKS delete request submitted for astrobase-test-eks cluster and nodegroups: test-nodegroup-cpu"
}
```

To destroy resources, simply use the same pattern, but with the `destroy` command.

```sh
$ astrobase destroy -f tests/assets/test-resources-gke.yaml
$ astrobase destroy -f tests/assets/test-resources-eks.yaml
```


### Preliminary Setup for AKS Cluster deployment

#### Configure your Azure Resource Group

```sh
$ az group create --name my-resource-group --location eastus
```

#### Create an Azure Active Directory Application and Register the Application to manage resources

Follow these links (assuming you have an admin owner configured as yourself already)

1. Register an application with Azure AD and create a service principal, https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal#app-registration-app-objects-and-service-principals
1. Assign a role to the application https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal#assign-a-role-to-the-application
1. https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal#get-tenant-and-app-id-values-for-signing-in
1. Authentication: Applciation Secret https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal#option-2-create-a-new-application-secret
1. https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal#configure-access-policies-on-resources

#### Export Azure Credentials in the shell session where you initialize astrobase

```sh
export AZURE_SUBSCRIPTION_ID=<AZURE_SUBSCRIPTION_ID>
export AZURE_CLIENT_ID=<AZURE_CLIENT_ID>
export AZURE_CLIENT_SECRET=<AZURE_CLIENT_SECRET>
export AZURE_TENANT_ID=<AZURE_TENANT_ID>
```

#### Initialize Astrobase

```sh
$ astrobase init
Initializing Astrobase ...
Starting Astrobase server ...
Astrobase initialized and running at http://localhost:8787
```

#### Check your versions

```sh
$ astrobase version; curl -s http://:8787/healthcheck | jq
🚀 Astrobase CLI 0.1.9 🧑‍🚀
{
  "api_version": "v0",
  "api_release_version": "0.1.5",
  "message": "We're on the air.",
  "time": "2021-04-17 02:11:51.255965"
}
```

#### Create Your AKS Cluster

```sh
$ astrobase apply -f tests/assets/test-aks-cluster.yaml -v "RESOURCE_GROUP_NAME=my_resource_group_name"
{
  "message": "AKS create request submitted for my_resource_group_name"
}
```

Check the status of the cluster until it shows `"Succeeded"`

```sh
$ curl -s -X GET "http://localhost:8787/aks/astrobase-test-aks?resource_group_name=my_resource_group_name" | jq .provisioning_state
"Succeeded"
```

#### Deploy Resources

```sh
$ astrobase apply -f tests/assets/test-resources-aks.yaml -v "RESOURCE_GROUP_NAME=my_resource_group_name"
applying resources to astrobase-test-aks@eastus
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
applying resources to astrobase-test-aks@eastus
deployment.apps/nginx-deployment created
```

#### Destroy Resources


```sh
$ astrobase destroy -f tests/assets/test-resources-aks.yaml -v "RESOURCE_GROUP_NAME=my_resource_group_name"
destroying resources in astrobase-test-aks@eastus
namespace "kubernetes-dashboard" deleted
serviceaccount "kubernetes-dashboard" deleted
service "kubernetes-dashboard" deleted
secret "kubernetes-dashboard-certs" deleted
secret "kubernetes-dashboard-csrf" deleted
secret "kubernetes-dashboard-key-holder" deleted
configmap "kubernetes-dashboard-settings" deleted
role.rbac.authorization.k8s.io "kubernetes-dashboard" deleted
clusterrole.rbac.authorization.k8s.io "kubernetes-dashboard" deleted
rolebinding.rbac.authorization.k8s.io "kubernetes-dashboard" deleted
clusterrolebinding.rbac.authorization.k8s.io "kubernetes-dashboard" deleted
deployment.apps "kubernetes-dashboard" deleted
service "dashboard-metrics-scraper" deleted
deployment.apps "dashboard-metrics-scraper" deleted
destroying resources in astrobase-test-aks@eastus
deployment.apps "nginx-deployment" deleted
```


#### Destroy Cluster

```sh
$ astrobase destroy -f tests/assets/test-aks-cluster.yaml -v "RESOURCE_GROUP_NAME=my_resource_group_name"
{
  "message": "AKS delete request submitted for astrobase-test-aks"
}
```

```sh
$ curl -s -X GET "http://localhost:8787/aks/astrobase-test-aks?resource_group_name=my_resource_group_name" | jq .provisioning_state
"Deleting"
```
