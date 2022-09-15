#! /bin/sh

RUN_TIME=`date +%Y%m%d%H%M%S`
CFG="fedavg_fedprox_dwa_hs_128_gc_10"
CLNT_CFG="fedavg_fedprox_dwa_hs_128_gc_10_per_client"

hdszs=(128)
for ((hs=0; hs<${#hdszs[@]}; hs++ ))
do
    nohup python -u federatedscope/main.py \
    --cfg  federatedscope/gfl/baseline/${CFG}.yaml \
    --client_cfg  federatedscope/gfl/baseline/${CLNT_CFG}.yaml \
    federate.save_to ${CFG}_${RUN_TIME}.pt \
    >  logs/${CFG}_hs_${hdszs[$hs]}_${RUN_TIME}.log 2>&1 &
done

