import datetime
import types

import boto3
import os

import handlers
import venv
import pip
from subprocess import call
import shutil

LAMBDA_CODE_DIR = 'lambda'
PROJECT_DIR = '..'
PIP_DEPS = PROJECT_DIR + '/../' + 'requirements.txt'

PROJECTS_MODULES = [
    'handlers',
    'helpers',
    'ieml',
    'models',
    'parser',
    'pipeline',
    'config.py'
]


def create_venv():
    venv.EnvBuilder(
        system_site_packages=False,
        clear=False,
        symlinks=False,
        upgrade=False,
        with_pip=True
    ).create('venv')


def install_dep():
    call(['venv/bin/pip3.5', 'install', '-r', PIP_DEPS])


def copy_project():
    if os.path.exists('project'):
        shutil.rmtree('project')

    os.makedirs('project')

    for module in PROJECTS_MODULES:
        src = '../../' + module
        dest = 'project/' + module

        if module == 'parser':
            dest = module

        if os.path.isdir(src):
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)


def create_handlers():
    with open('handler_python.py', 'w') as fp:
        fp.write(
"""import subprocess
import cPickle as pickle

def lambda_handler(event, context):
   pickle.dump( event, open( '/tmp/event.p', 'wb' ) )
   args = ('venv/bin/python3.5', 'project/handler.py', context.function_name)
   popen = subprocess.Popen(args, stdout=subprocess.PIPE)
   popen.wait()
   output = popen.stdout.read()
   print(output)

""")

    endpoints = {t: v for t, v in handlers.__dict__.items() if isinstance(v, types.FunctionType)}

    with open('project/handler.py', 'w') as fp:
        fp.write(
"""
import sys
import handlers
import pickle

event = pickle.load( open( '/tmp/event.p', 'rb' ) )
print(handlers.__dict__[sys.argv[1]].__call__(**event))

"""
)


def upload_zip_s3():
    call(['zip', '-r', '/tmp/lambda_server.zip', 'venv', 'parser', 'project', 'handler_python.py'])
    s3 = boto3.resource('s3')
    data = open('/tmp/lambda_server.zip', 'rb')
    name = 'lambda-'+str(datetime.datetime.now())
    print('---> uploading lambda to AWS S3 at intlekt-lambda-zip/' + name)
    s3.Bucket('intlekt-lambda-zip').put_object(Key=name, Body=data)


# upload zip in bucket
# create IAM
# set up db on ebs
# create each lambda func
# create API gatway
# test


def create_lambda(name):
    client = boto3.client('lambda')

    s3 = boto3.resource('s3')
    lambda_key = sorted(s3.Bucket('intlekt-lambda-zip').objects.all(), key=lambda o: o.last_modified, reverse=True)[0].key

    try:
        res = client.get_function(FunctionName=name)
    except Exception:
        res = None

    if res:
        print('---> updating code of lambda "%s" with intlekt-lambda-zip/%s'%(name, lambda_key))

        response = client.update_function_code(
            FunctionName=name,
            S3Bucket='intlekt-lambda-zip',
            S3Key=lambda_key,
            Publish=True
        )
        print(response)
    else:
        print('---> creating lambda "%s" with code in intlekt-lambda-zip/%s'%(name, lambda_key))

        response = client.create_function(
            FunctionName=name,
            Runtime='python2.7',
            Role='arn:aws:iam::114187237923:role/service-role/lambdaRoleMicroService',
            Handler='handler_python.lambda_handler',
            Code={
                'S3Bucket': 'intlekt-lambda-zip',
                'S3Key': lambda_key,
            },
            Description=name + ' endpoint',
            Timeout=3,
            MemorySize=128,
            Publish=True
        )
        print(response)


if not os.path.exists(LAMBDA_CODE_DIR):
    os.makedirs(LAMBDA_CODE_DIR)
os.chdir(LAMBDA_CODE_DIR)

if not os.path.exists('venv'):
    create_venv()


#
# install_dep()
# copy_project()
# create_handlers()
# upload_zip_s3()
create_lambda('basic_test')