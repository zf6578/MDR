#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import OrderedDict
import logging
import torch
import copy
from torch import Tensor
logging.getLogger().setLevel(logging.INFO)

class AdapParameterServer:
    def __init__(self, init_model: OrderedDict[str, Tensor], state=None, params=None, optimizer=None):
        self.model_queue = []
        self.iteration = 0
        self.opt_name = params.get('opt_name', 'sgd')
        self.client_number = params.get('client_number', None)
        self.momentum =params.get('momentum', 0)
        self.optimizer_param = params.get('optimizer_param', None)
        self.optimizer_init = optimizer
        self.logger = logging
        assert self.optimizer_init and self.client_number and params is not None
        self.init_server(init_model)

    def push_client(self, model_dict: OrderedDict[str, Tensor]):
        self.model_queue.append(model_dict)

    def pop_client(self):
        self.model_queue.pop()

    def init_server(self, init_model):
        self.global_model = copy.deepcopy(init_model)
        self.optimizer = self.optimizer_init(self.global_model.values(), **self.optimizer_param)

    def aggregation(self):
        assert len(self.model_queue) == self.client_number
        self.logger.info("Aggregator - star Aggregator with {} client.".format(len(self.model_queue)))
        grad_list = [torch.zeros_like(self.global_model[x], memory_format=torch.preserve_format).float() for x in self.global_model]
        momentum_tensor_list = [torch.zeros_like(self.global_model[x], memory_format=torch.preserve_format).float() for x in self.global_model]
        self.optimizer.zero_grad()
        for local_state_dict in self.model_queue:
            for grad_tensor, local_tensor in zip(grad_list, local_state_dict.values()):
                grad_tensor.add_(local_tensor)
        for grad_tensor, global_tensor, momentum_tensor in zip(grad_list, self.global_model, momentum_tensor_list):
            grad_tensor.div_(len(self.model_queue))
            grad_tensor = -grad_tensor
            grad_tensor.add_(self.global_model[global_tensor])
            if self.momentum > 0:
                grad_tensor.copy_(momentum_tensor * self.momentum + grad_tensor * (1 - self.momentum))
                momentum_tensor.copy_(grad_tensor)
            self.global_model[global_tensor].grad = grad_tensor
        self.optimizer.step()
        self.iteration += 1
        del self.model_queue[:]
