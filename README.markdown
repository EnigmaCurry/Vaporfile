Vaporfile
==========

Vaporfile is a tool to upload and synchronize static websites to the
[Amazon S3](http://aws.amazon.com/s3/) cloud.

*WARNING*: This is alpha quality software, version 0.0.1. It works for
me, but it may destroy your life. Be careful, test this out with
non-important data first. I doubt I've done anything royally stupid
here, but I guess it's technically possible that some unforseen bug could delete
all of the buckets configured in your S3 account. YOU'VE BEEN WARNED.

Requirements
------------
* [Python 2.6](http://www.python.org/download/) or above.
* An [Amazon S3 account](http://aws.amazon.com/s3/).
* The DEV version of [boto](https://github.com/boto/boto) (until 2.0b5
or greater is released).

Install
-------

As of Feb 19 2011, the new [S3 website
extensions](http://aws.typepad.com/aws/2011/02/host-your-static-website-on-amazon-s3.html)
are one day old, needless to say, it's a bit bleeding edge. Vaporfile
depends on the best Python bindings for Amazon S3:
[boto](https://github.com/boto/boto). The boto devs are really on top
of their game and have already implemented the website features, but
they haven't made it into a realeased version yet. For now, you'll
need to install the dev version:

     git clone https://github.com/boto/boto.git
     sudo python boto/setup.py develop

Now you can install the DEV version of Vaporfile:

    git clone https://github.com/EnigmaCurry/Vaporfile.git
    sudo python vaporfile/setup.py develop

Or, you can install the packaged version on PyPI (Not there yet):

    sudo easy_install vaporfile
    
Uploading a website
-------------------

Once Vaporfile is installed, you can run it to create a new website
configuration:

        vaporfile create

This will run a configuration wizard that will get you started. It
just asks you a few questions to get setup:

* Asks you for your [Amazon AWS
  credentials](https://aws-portal.amazon.com/gp/aws/developer/account/index.html?action=access-key).
* Configures your domain name / Amazon S3 bucket name.
* Configures the path of the website on your local drive.
* Configures the index page of your site (eg. index.html)
* Configures the 404 error page of your site.
* Creates the actual bucket on S3 and enables the website endpoint.

It saves all this configuration information in `~/.vaporfile`,
which includes your AWS credentials in plain text. The file is marked as readable
only by your user account, so this should be reasonably safe on
machines you control/trust.

Once you've created the site, you can upload it:

     vaporfile -v upload [name-of-website]

With the -v flag on, you'll see all the files it's uploading,
otherwise it should silently complete.

Now make any changes you wish to your site locally, and run the upload
again. Files that have changed will get re-uploaded, files that have
been deleted locally will get deleted from S3 (unless you specify --no-delete).

Deployment
----------

Vaporfile will upload your site to Amazon, but you still need to
configure your domain to point to it.

The name you chose for your website when running `vaporfile create`
is the bucket name created on S3. S3 creates a domain like this:

    www.yourdomain.com.s3-website-us-east-1.amazonaws.com

Assuming you don't like that domain name, you'll probably want to
point your own domain name to that location. You do that with a CNAME
configured with your DNS provider -- create a CNAME record for
`www.yourdomain.com` and point it to `s3-website-us-east-1.amazonaws.com`.

Usage
-----

You can see the rest of the usage by running `vaporfile -h`, but here
it is:

    usage: vaporfile [-h] [--version] [-c PATH] [-v] [-vv]
                     {credentials,create,list,upload} ...
    
    positional arguments:
      {credentials,create,list,upload}
        credentials         Manage Amazon AWS credentials
        create              Create a new S3 website
        upload              Upload a previously configured website
        list                List all configured websites
    
    optional arguments:
      -h, --help            show this help message and exit
      --version
      -c PATH, --config PATH
                            Use alternative config file (defaults to ~/.vaporfie)
      -v, --verbose         Be verbose
      -vv, --veryverbose    Be extra verbose
