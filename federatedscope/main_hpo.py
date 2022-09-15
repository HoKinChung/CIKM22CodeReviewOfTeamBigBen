import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

from emukit.test_functions import forrester_function
from emukit.core import ContinuousParameter, CategoricalParameter, ParameterSpace
from emukit.examples.gp_bayesian_optimization.single_objective_bayesian_optimization import GPBayesianOptimization
from yacs.config import CfgNode
from federatedscope.core.auxiliaries.data_builder import get_data
from federatedscope.core.configs.config import global_cfg
from federatedscope.core.cmd_args import parse_args
from federatedscope.core.auxiliaries.utils import setup_seed, update_logger
from federatedscope.core.auxiliaries.worker_builder import get_client_cls, get_server_cls
from federatedscope.core.fed_runner import FedRunner


### --- Figure config
LEGEND_SIZE = 15


DEV_MODE = False  # simplify the federatedscope re-setup everytime we change
# the source codes of federatedscope
if DEV_MODE:
    file_dir = os.path.join(os.path.dirname(__file__), '..')
    sys.path.append(file_dir)

if os.environ.get('https_proxy'):
    del os.environ['https_proxy']
if os.environ.get('http_proxy'):
    del os.environ['http_proxy']

def eval_fl_algo(x, data, init_cfg, client_cfg):
    
    init_cfg.merge_from_list(["train.optimizer.lr", float(x[0])])

    # it will print the config 
    init_cfg.freeze()

    runner = FedRunner(data=data,
                       server_class=get_server_cls(init_cfg),
                       client_class=get_client_cls(init_cfg),
                       config=init_cfg.clone(),
                       client_config=client_cfg)
    results = runner.run()

    # so that we could modify cfg in the next trial
    init_cfg.defrost()

    return [results['client_summarized_weighted_avg']['test_avg_loss']]

def out_target_func(x):
    init_cfg = global_cfg.clone()
    args = parse_args()
    init_cfg.merge_from_file(args.cfg_file)
    init_cfg.merge_from_list(args.opts)

    update_logger(init_cfg)
    setup_seed(init_cfg.seed)

    # load clients' cfg file
    client_cfg = CfgNode.load_cfg(open(args.client_cfg_file,
                                       'r')) if args.client_cfg_file else None

    # federated dataset might change the number of clients
    # thus, we allow the creation procedure of dataset to modify the global
    # cfg object
    data, modified_cfg = get_data(config=init_cfg.clone())
    init_cfg.merge_from_other_cfg(modified_cfg)

    return np.asarray([eval_fl_algo(elem, data, init_cfg, client_cfg) for elem in x])

def main():
    target_function = out_target_func
    space = ParameterSpace([ContinuousParameter('lr', 1e-4, .75)])
    x_plot = np.linspace(space.parameters[0].min, space.parameters[0].max,
                         200)[:, None]
    #y_plot = target_function(x_plot)
    X_init = np.array([[0.005], [0.05], [0.5]])
    Y_init = target_function(X_init)

    bo = GPBayesianOptimization(variables_list=space.parameters,
                                X=X_init,
                                Y=Y_init)
    bo.run_optimization(target_function, 15)

    mu_plot, var_plot = bo.model.predict(x_plot)

    plt.figure(figsize=(12, 8))
    plt.plot(bo.loop_state.X,
             bo.loop_state.Y,
             "ro",
             markersize=10,
             label="Observations")
    #plt.plot(x_plot, y_plot, "k", label="Objective Function")
    #plt.plot(x_plot, mu_plot, "C0", label="Model")
    plt.fill_between(x_plot[:, 0],
                     mu_plot[:, 0] + np.sqrt(var_plot)[:, 0],
                     mu_plot[:, 0] - np.sqrt(var_plot)[:, 0],
                     color="C0",
                     alpha=0.6)

    plt.fill_between(x_plot[:, 0],
                     mu_plot[:, 0] + 2 * np.sqrt(var_plot)[:, 0],
                     mu_plot[:, 0] - 2 * np.sqrt(var_plot)[:, 0],
                     color="C0",
                     alpha=0.4)

    plt.fill_between(x_plot[:, 0],
                     mu_plot[:, 0] + 3 * np.sqrt(var_plot)[:, 0],
                     mu_plot[:, 0] - 3 * np.sqrt(var_plot)[:, 0],
                     color="C0",
                     alpha=0.2)
    plt.legend(loc=2, prop={'size': LEGEND_SIZE})
    plt.xlabel(r"$x$")
    plt.ylabel(r"$f(x)$")
    plt.grid(True)
    plt.xlim(0, 0.75)

    #plt.show()
    plt.savefig("winston_bbo.pdf", bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    main()

    

    

    
