import sys
import os, os.path
import logging
import readline
import getpass

from boto.s3.key import Key

import credentials
import config
import s3_util
import util
from prompt_util import get_yes_no, get_input, clear_screen

logger = logging.getLogger("vaporfile.website")

def prompt_create_website(args):
    #This is the information we'll gather:
    user_config = None
    bucket_name = None
    using_own_domain = None
    sync_path = None
    directory_index = None
    error_index = None
    
    clear_screen()
    print(" Amazon S3 Website Creation Wizard ".center(80,"+"))
    print("This will guide you through the process of creating a new website on Amazon S3.")
    print("No changes to your S3 account will occur until you accept changes at the end.")
    print("You may press Ctrl-C at any point to quit without saving.")
    print("".center(80,"+"))
    print("")
    try:
        user_config = config.load_config()
    except IOError:
        print("No existing account information found.")
        if get_yes_no("Would you like to setup your Amazon AWS account? [Y/n] : ",default=True):
            credentials.prompt_save_credentials({})
        else:
            print("")
            print("Cannot proceed without Amazon account information.")
            sys.exit(1)
        user_config = config.load_config()
    conn = s3_util.get_connection()
    using_own_domain = get_yes_no("Will you be using your own domain name? [y/n] : ")
    if using_own_domain:
        print("")
        print("Amazon S3 websites hosted using your own domain require a CNAME configured")
        print("with your DNS service. Unfortunately, this means that you cannot use your root")
        print("domain with S3, you must use a subdomain.")
        print("")
        while True:
            bucket_name = get_input("What is the the fully qualified subdomain you would like to use?\n[eg. www.yourdomain.com] : ",accept_blank=False)
            print("Checking to see if {0} is available...".format(bucket_name))
            if not s3_util.test_bucket_exists(conn, bucket_name):
                break
            print("")
            #The bucket already exists.. by the user?
            if bucket_name in s3_util.get_bucket_names(conn):
                print("Sorry, it looks like you've already configured a website with that domain.")
            else:
                print("Sorry, it looks like someone else owns that bucket name. Contact Amazon support")
                print("for help if you own the domain you chose. This is an unfortunate side-effect of")
                print("Amazon choosing a globally flat namespace for buckets.")
                print("")        
    else:
        print("")
        print("Without using your own domain, you will need to create a unique bucket name.")
        print("You will only be able to access your website through the bucket address")
        print("Amazon provides, which is a bit long and cumbersome.")
        print("Example: yourwebsite.s3-website-us-east-1.amazonaws.com")
        print("")
        while True:
            bucket_name = get_input("What is the bucket name you would like to use?\n[eg. yourwebsite] : ")
            print("Checking to see if {0} is available...".format(bucket_name))
            if not s3_util.test_bucket_exists(conn, bucket_name):
                break
            print("")
            print("Sorry, that bucketname is already used. Try another.")
    clear_screen()
    print(" Local Path Selection ".center(80,"+"))
    print("This tool works by synchronizing a local directory to your S3 bucket.")
    print("Each time you synchronize, this tool will upload new or changed files")
    print("as well as delete any files no longer found in the local directory.")
    print("".center(80,"+"))
    print("")
    while True:
        sync_path = get_input("What is the full local directory path you want "
                              "synchronized?\n[eg. /home/{0}/website ] : ".\
                                  format(getpass.getuser()), accept_blank=False)
        if os.path.isdir(sync_path):
            break
        elif os.path.isfile(sync_path):
            print("Sorry, that's not a directory. Please try again.")
        else:
            if get_yes_no("This directory does not exist. Would you like to create it? (y/n)"):
                try:
                    util.mkdir(sync_path)
                except OSError:
                    print("Permission denied. Try again.")
                else:
                    break
        print("")
    clear_screen()
    print(" Confirmation Options ".center(80,"+"))
    print("")
    if get_yes_no("Would you like to use index.html as your default index file? (Y/n)", default=True):
        directory_index = "index.html"
    else:
        while True:
            print("What file would you like to serve when directories are requested?")
            directory_index = get_input("[eg. index.html] : ")
            if directory_index != "":
                break
            print("You must enter a directory index. Most users should choose index.html")
    print("")
    if get_yes_no("Would you like a special 404 handler when files aren't found? (y/N) : ", default=False):
        while True:
            print("What file would you like to serve when files aren't found?")
            error_index = get_input("[eg. 404.html] : ")
            if error_index != "":
                break            
        print("")
    clear_screen()
    print(" Confirmation ".center(80,"+"))
    print("OK, we've gathered all the necessary information about your new website.")
    print("Let's review:")
    print("")
    if using_own_domain:
        print("    Your domain name:".ljust(35)+bucket_name)
    print("    Amazon S3 bucket name:".ljust(35)+bucket_name)
    print("    Local path to synchronize:".ljust(35)+sync_path)
    print("    Index file:".ljust(35)+directory_index)
    if error_index:
        print("    Error index file:".ljust(35)+error_index)
    print("")
    if get_yes_no("Would you like to save this configuration now? [y/n] : "):
        website = S3Website(
            bucket_name, sync_path, index=directory_index,
            error_doc=error_index)
        user_config["websites"][bucket_name] = website.to_config()
        website.create()
        print("Amazon S3 Bucket created!")
        config.save_config(user_config)
        print("Website configuration saved!")
        print("Your Amazon website endpoint: http://{0}.s3-website-us-east-1."
              "amazonaws.com".format(bucket_name))
        if using_own_domain:
            print("Your DNS service needs a CNAME record pointing {0} "
                  "to\ns3-website-us-east-1.amazonaws.com".format(bucket_name))
            print("")
        print("To upload your website run this command:")
        print("")
        print("  vaporfile -v upload {0}".format(bucket_name))
        print("")

def upload_website(args):
    try:
        user_config = config.load_config()
    except IOError:
        print("")
        print("Can't find a configuration. You need to run: vaporfile create")
        print("")
        return
    try:
        website = S3Website.from_config(user_config["websites"][args.WEBSITE])
    except KeyError:
        print("")
        print("Can't find a website configuration called {0}".format(args.WEBSITE))
        print("Maybe you need to create it first?")
        return
    website.synchronize(delete=not args.no_delete)

def list_websites(args):
    try:
        user_config = config.load_config()
    except IOError:
        print("")
        print("Can't find a configuration. You need to run: vaporfile create")
        print("")
        return
    if len(user_config["websites"]) == 0:
        print("")
        print("No websites have been created yet. You need to run: vaporfile create")
        print("")
        return
    for name, website in user_config["websites"].items():
        print(("   "+name).ljust(25)+"- "+website["localpath"])
        
                
class S3Website(object):
    """Tool for maintaining a static website in S3"""
    def __init__(self, bucketname, localpath, index="index.html",
                 error_doc="404.html",**kwargs):
        self.bucketname = bucketname
        self.localpath = localpath
        self.index = index
        self.error_doc = error_doc
    def to_config(self):
        return {"bucketname":self.bucketname,
                "localpath":self.localpath,
                "index":self.index,
                "error_doc":self.error_doc}
    @classmethod
    def from_config(cls, config_dict):
        return cls(**config_dict)
    def get_bucket(self):
        return self.get_connection().get_bucket(self.bucketname)
    def get_connection(self):
        return s3_util.get_connection()
    def create(self):
        """Create the bucket for the subdomain."""
        #Check if the bucket name already exists in our account,
        #boto doesn't tell us this.
        connection = self.get_connection()
        if self.bucketname in s3_util.get_bucket_names(connection):
            raise Exception("Bucket '{0}' already exists in your account.")
        bucket = connection.create_bucket(self.bucketname)
        logger.info("Created new bucket : {0}".format(self.bucketname))
        #A website should be publically readable:
        bucket.set_acl("public-read")
        #Turn on website functionality:
        if self.error_doc:
            bucket.configure_website(self.index, self.error_doc)
        else:
            bucket.configure_website(self.index)
    def synchronize(self, delete=False):
        """Synchronize the localpath to S3.

        Upload new or changed files.
        Delete files that no longer exist locally."""
        bucket = self.get_bucket()
        s3_paths = s3_util.get_paths_from_keys(bucket)
        local_files = set()
        for dirpath, dirnames, filenames in os.walk(self.localpath):
            for filename in filenames:
                file_path = os.path.join(dirpath,filename)
                file_key = os.path.relpath(file_path,self.localpath)
                if os.sep == "\\":
                    #Windows paths need conversion
                    local_files.add(file_key.replace("\\","/"))
                else:
                    local_files.add(file_key)
                try:
                    s3_key = s3_paths[file_key]
                except KeyError:
                    #File is new
                    s3_key = bucket.new_key(file_key)
                    logger.info("Uploading new file: {0}".format(file_key))
                    s3_key.set_contents_from_filename(file_path)
                    s3_key.set_acl("public-read")
                else:
                    #File already exists, check if it's changed.
                    local_md5 = util.md5_for_file(file_path)
                    if local_md5 != s3_key.etag.replace("\"",""):
                        #File has changed
                        logger.info("Uploading changed file: {0}".format(file_key))
                        s3_key.set_contents_from_filename(file_path)
        if delete:
            #Delete all files that don't exist locally
            for name, key in s3_paths.items():
                if name not in local_files:
                    #Delete it.
                    logger.info("Deleting old file: {0}".format(name))
                    key.delete()
                
