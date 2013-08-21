Nimbostratus
============

Tools for fingerprinting and exploiting Amazon cloud infrastructures. These tools are a PoC which I developed for my "Pivoting in Amazon clouds" talk, developed using the great [boto](https://github.com/boto/boto) library for accessing Amazon's API.

Feel free to report bugs, fork and send pull-requests. You can also drop me a line at [@w3af](https://twitter.com/w3af).

Installation
============

```bash
git clone git@github.com:andresriancho/nimbostratus.git
cd nimbostratus
pip install -r requirements.txt
```


Usage
=====

A note on boto
--------------

It's important to notice that our tools use [boto](https://github.com/boto/boto) for connecting to Amazon's API, which
means that you'll have to know at least the basics about how to provide credentials to it. There are basically three
ways you can provide credentials to boto/nimbostratus:

 * `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` [environment variables](https://code.google.com/p/boto/wiki/BotoConfig)
 * `~/.boto` [file](https://code.google.com/p/boto/wiki/BotoConfig)
 * [Instance meta-data / instance profile](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/UsingIAM.html#UsingIAMrolesWithAmazonEC2Instances)

In other words, you either export the environment variables with the values you captured from the target Amazon infrastructure,
you write them to the `~/.boto` configuration file or run this tool inside a EC2 instance which has been configured to use and instance profile
and allow boto to extract credentials from the meta-data.


IAM role permissions
--------------------

This tool will dump all IAM role permissions for a set of credentials (API key and secret or instance-profile). This tool is commonly used when you just gain access to an EC2 instance and want to know which permissions are available for you.

```console
$ dump-role-permissions.py
...
```

Extract credentials
-------------------

Uses boto to identify the credentials available in this instance and prints them out to the console.

```console
$ dump-credentials.py
...
```

Once you've got the credentials from an EC2 instance you've exploited, you can continue to work from any other
host with internet access (remember: EC2 instances are in many cases spawned for a specific work and then terminated).

Dump instance meta-data
-----------------------

All EC2 instances have [meta-data](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AESDG-chapter-instancedata.html)
which is accessible via [http://169.254.169.254/latest/meta-data/](http://169.254.169.254/latest/meta-data/). This
tool will extract all the important information from the metadata and show it to you.

```console
$ dump-ec2-metadata.py
...
```

Create DB snapshot
------------------

In some cases you've got Amazon credentials which allow you to access the [RDS](http://aws.amazon.com/rds/) API but
don't have any access to the database itself (MySQL user). This tool allows you to access the information stored in
that database by creating a snapshot and restoring it.

```console
$ snapshot-rds.py --password=foobar
...
```

Inject raw Celery message
-------------------------

Celery warns developers about the [insecure pickle](http://docs.celeryproject.org/en/latest/userguide/security.html#serializers)
serialization method, but of course you'll find deployments like this in real life. This tool will check if the instance
where this tool is being run has access to SQS, if that SQS has a Celery queue, verify that the Queue is using pickle and
finally inject a raw message that will execute arbitrary commands when un-pickled.

```console
$ celery-unpickle-exploit.py
...
```

Create new user
---------------

If you've got credentials which allow you to create a new user using [IAM](http://aws.amazon.com/iam/) this tool will
create it (with permissions to access all Amazon resources) and return API key and secret.

```console
$ create-iam-user.py
...
```



What's a `nimbostratus` anyways?
================================

[nimbostratus](http://en.wikipedia.org/wiki/Nimbostratus_cloud) is a type of cloud, if you ever started a project you know how hard it is to name it... so I just chose something that sounded "cool" and was "cloud-related".
