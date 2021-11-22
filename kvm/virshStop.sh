#!/bin/bash

botVms="RunescapeBot RunescapeBot2"

for next in $botVms;
do
  echo "stopping bot on $next"
  ip=$(virsh domifaddr $next | sed -n '3 p' | cut -d " " -f 21)
  ip=${ip::-3}
  ssh -i shared_id_rsa dave@${ip} 'bash -c "killall mineTest.py"' &
done
