#!/bin/bash

from=$1
to=$2

scp -i shared_id_rsa dave@$from dave@$to
