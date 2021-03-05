from models.models import *
from pipelines.run_dqn import train, evaluate
import matplotlib.pyplot as plt
import yaml

with open("config.yml", "r") as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)

def load_weights(model:DQN, IN_PATH):
    model.policy_net.load_state_dict(torch.load(IN_PATH))
    model.transfer_weights()
    return model

def save_weights(model:DQN, OUT_PATH):
    torch.save(model.target_net.state_dict(), OUT_PATH)
    return


def run_evaluations(model:DQN, index:str, symbol:str, dataset:str):
    # def run_evaluations(model:DQN, dataset:str, eval_set:str):
    rewards, profits, running_profits, total_profits = evaluate(model,
                                                       index=index,
                                                       symbol=symbol,
                                                       strategy=1,
                                                       dataset=dataset)
    hold_rewards, hold_profits, hold_running_profits, hold_total_profits = evaluate(model,
                                                                      index=index,
                                                                      symbol=symbol,
                                                                      dataset=dataset,
                                                                      strategy=0,
                                                                      strategy_num=1.0,
                                                                      only_use_strategy=True)

    print(f"TOTAL MKT PROFITS : {hold_total_profits}")
    print(f"TOTAL MODEL PROFITS : {total_profits}")
    plt.plot(list(range(len(running_profits))), running_profits, label="Model strategy")
    plt.plot(list(range(len(hold_running_profits))), hold_running_profits, label="Buy and hold")
    plt.legend()
    plt.savefig("plots/evaluation.png")
    plt.title("Eval Profits")
    plt.show()

def run_training(model:DQN, index: str, symbol:str, dataset:str):
    model, losses, rewards, val_rewards, profits, val_profits = train(model=model, index=index, symbol=symbol, dataset=dataset)

    plt.plot(list(range(len(losses))), losses)
    plt.title("Losses")
    plt.savefig("plots/losses.png")
    plt.show()

    plt.plot(list(range(len(rewards))), rewards, label="Training")
    plt.plot(list(range(len(val_rewards))), val_rewards, label="Validation")
    plt.title("Rewards")
    plt.savefig("plots/rewards.png")
    plt.legend()
    plt.show()

    plt.plot(list(range(len(profits))), profits, label="Training")
    plt.plot(list(range(len(val_profits))), val_profits, label="Validation")
    plt.title("Total Profits")
    plt.savefig("plots/profits.png")
    plt.legend()
    plt.show()

def run_experiment(**kwargs):
    model = DQN(method=experiment_args['method'])

    if kwargs['load_model'] and kwargs['IN_PATH']:
        model = load_weights(model=model, IN_PATH=kwargs['IN_PATH'])

    if kwargs['train_model'] and kwargs['train_set']:
        run_training(model=model, index=kwargs['index'], symbol=kwargs['symbol'], dataset=kwargs['train_set'])

        if kwargs['save_model'] and kwargs['OUT_PATH']:
            save_weights(model=model, OUT_PATH=kwargs['OUT_PATH'])

    if kwargs['eval_model'] and kwargs['eval_set']:
        run_evaluations(model=model, index=kwargs['index'], symbol=kwargs['symbol'], dataset=kwargs['eval_set'])

if __name__ == '__main__':
    # Input your experiment params
    experiment_args = {
        'method': NUMQ,
        'index': 'gspc',
        'symbol': '^GSPC',
        'train_model': True,
        'eval_model': True,
        'train_set': 'train',
        'eval_set': 'valid',
        'load_model': False,
        'IN_PATH': 'weights/numq_gspc_10.pt',
        'save_model': False,
        'OUT_PATH': 'weights/numq_gspc_10.pt'
    }

    run_experiment(**experiment_args)
