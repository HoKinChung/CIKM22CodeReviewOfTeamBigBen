### Reproduce the Result

At first please alter the `data.root` in `federatedscope/gfl/baseline/fedavg_fedprox_dwa_hs_128_gc_10.yaml` the actual path to data.

Then run the following script
```shell
sh fedavg_fedprox_dwa_hs_128_gc_10.sh
```

After the training and prediction are completed, you can find the result in `exp/FedAvg_gin_on_cikmcup_lr0.1_lstep15_hdsz128_drpt0.3_/sub_exp_20220908103731/prediction.csv`

### Introduction of developed algorithm

We used the `fedavg` and `fedprox` algorithms and fine-tuned the hyper parameters