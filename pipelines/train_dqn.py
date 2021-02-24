import numpy as np
import torch
import random
from typing import Tuple
from collections import deque
import torch.nn.functional as F
from torch.optim import Adam
from torch import optim, Tensor

from .build_batches import get_episode
from utils.rewards import compute_reward
from models.models import NumQModel, NumQDRegModel, DQN




"""
TODO fill in DQN details
"""
L = 10
LR = 0.0001
BATCH_SIZE = 64
GAMMA = 0.05
THRESHOLD = 0.2
#TODO: Do we need this and what do we set it to?
MEMORY_CAPACITY = 3000
MIN_MEMORY_CAPACITY = 200
STRATEGY = 0

class ReplayMemory(object):
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)

    def update(self, transition: Tuple[Tensor, int, Tensor, float]):
        """
        Saves a transition
        :param transition: (state, action_index, next_state, reward)
        :return:
        """
        self.memory.append(transition)

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

# Select an action given model and state
# Returns action index
def select_action(model: DQN, state: Tensor, strategy: int=STRATEGY):
    # Get q values for this state
    with torch.no_grad():
        q, num = model.policy_net(state)
    
    # Reduce unnecessary dimension
    q = q.squeeze()
    num = num.squeeze()

    # TODO check (q.shape num.shape should be (3,) (1,) respectively) here
    assert q.shape() == (3, )
    assert num.shape() == (1, )

    if strategy is not None:
        # Use predefined confidence if confidence is too low, indicating a confused market
        confidence = (torch.abs(q[model.BUY] - q[model.SELL]) / torch.sum(q)).item()
        if confidence < THRESHOLD:
            # TODO use defined strategy (hold for now)
            # actions = torch.where(confidences.lt(threshold), strategy, best_q)
            # return model.HOLD, num.item()
            return strategy, num.item()
    
    # If confidence is high enough, return the action of the highest q value
    return torch.argmax(q).item(), num.item()

# Update policy net using a batch from memory
def optimize_model(model: DQN, memory: ReplayMemory):
    # Skip if memory length is not at least batch size
    if len(memory) < BATCH_SIZE:
        return

    # Initialize optimizer
    optimizer = optim.Adam(model.policy_net.params(),lr=LR)

    # Sample a batch from memory
    # (state, action_index, next_state, reward)
    batch = list(zip(memory.sample(batch_size=BATCH_SIZE)))

    # Get batch of states, actions, and rewards
    # (each item in batch is a tuple of tensors so stack puts them together)
    state_batch = torch.stack(batch[0])
    action_batch = torch.stack(batch[1])
    next_state_batch = torch.stack(batch[2])
    reward_batch = torch.stack(batch[3])

    # TODO check shape is (BATCH_SIZE, 200), (BATCH_SIZE, 1), (BATCH_SIZE, 200), (BATCH_SIZE, 1) respectively
    assert state_batch.shape() == (BATCH_SIZE, 200)
    assert action_batch.shape() == (BATCH_SIZE, 1)
    assert next_state_batch.shape() == (BATCH_SIZE, 200)
    assert reward_batch.shape() == (BATCH_SIZE, 1)

    # Get q values from policy net from state batch
    # (we keep track of gradients for this model)
    q_batch, num_batch = model.policy_net(state_batch)

    # Get q values from target net from next states
    # (we do NOT keep track of gradients for this model)
    # TODO handle terminal state in build_episode and then here.
    next_q_batch, next_num_batch = model.target_net(state_batch)

    # TODO check size of all outputs

    # Compute the expected Q values
    expected_q_batch = reward_batch + (GAMMA * next_q_batch)

    # Loss is the difference between the q values from the policy net and expected q values from the target net
    loss = F.smooth_l1_loss(q_batch, expected_q_batch)

    # Clear gradients and update model parameters
    optimizer.zero_grad()
    loss.backward()
    # TODO need gradient clipping?
    #  RESPONSE: I think we smooth l1 loss takes care of that
    #  https://srome.github.io/A-Tour-Of-Gotchas-When-Implementing-Deep-Q-Networks-With-Keras-And-OpenAi-Gym/
    optimizer.step()

    return loss.item()


def train(model: DQN, dataset: str, num_episodes: int, memory_capacity: int=MEMORY_CAPACITY, strategy: int=STRATEGY):
    losses = []
    replay_memory = ReplayMemory(capacity=memory_capacity)

    # Run for the defined number of episodes
    for e in range(num_episodes):
        # TODO need to figure out what episode should be
        # episode:= list of (state, next_state, price, prev_price, init_price) in the training set
        train, valid, test = get_episode(dataset=dataset)

        for sample in train:
            # get the sample
            #TODO: code breaks down here
            (state, next_state, price, prev_price, init_price) = sample
            # Select action
            action_index, num = select_action(model=model, state=state, strategy=strategy)

            # Get action values from action indices (BUY=1, HOLD=0, SELL=-1)
            action_value = model.action_index_to_value(action_index=action_index)

            # Get reward given action_value and num
            reward = compute_reward(num_t=num, action_value=action_value, price=price,
                                    prev_price=prev_price, init_price=init_price)

            # Push transition into memory buffer
            # NOTE (using action index not action value)
            replay_memory.update((state, action_index, next_state, reward))

            # Update model and add loss to losses
            loss = optimize_model(model=model, memory=replay_memory)
            losses.append(loss)

        # Update policy net with target net
        model.transfer_weights()
    
    # Return loss values during training
    return losses
