#!/bin/bash

botVms="RunescapeBot RunescapeBot2"

#first start all the vms
for next in $botVms;
do
  echo "starting $next"
  virsh start $next
done
#sleep some to make sure they finish booting
sleep 10

#now tell each vm to start the bot
for next in $botVms;
do
  ip=$(virsh domifaddr $next | sed -n '3 p' | cut -d " " -f 21)
  ip=${ip::-3}
  ssh -i shared_id_rsa dave@${ip} 'bash -c "cd ~/projects/chadbot && DISPLAY=:0 ./python/scripts/loginTest.py config/chadsButts.config && DISPLAY=:0 ./python/scripts/mineTest.py config/chadsButts.config"' &
done
