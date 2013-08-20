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

IAM role permissions
--------------------

This tool will dump all IAM role permissions for a set of credentials (API key and secret or instance-profile).

```console
$ dump-role-permissions.py
...
```


What's a nimbostratus anyways?
==============================

[nimbostratus](http://en.wikipedia.org/wiki/Nimbostratus_cloud) is a type of cloud, if you ever started a project you know how hard it is to name it... so I just chose something that sounded "cool" and was "cloud-related".
