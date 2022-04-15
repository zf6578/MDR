import unittest
from collections import OrderedDict
import yaml
from torch.nn.modules import MSELoss
from torch.autograd import Variable
import torch.nn.functional as F
import torch
from torch.optim import Adam, Adadelta, Adagrad
from torch.optim.sgd import SGD
from Adaptive_parameter_server import AdapParameterServer

class Net(torch.nn.Module):
    def __init__(self, n_feature, n_hidden, n_output):
        super(Net, self).__init__()
        self.hidden = torch.nn.Linear(n_feature, n_hidden)
        self.predict = torch.nn.Linear(n_hidden, n_output)

    def forward(self, x):
        x = F.sigmoid(self.hidden(x))
        x = self.predict(x)
        return x

def parser_cfg(cfg_file):
    try:
        return yaml.safe_load(open(cfg_file))
    except:
        return None

class TestAdaptiveagg(unittest.TestCase):

    def setUp(self) -> None:

        global_model = Net(1, 5, 1)
        client_model_1 = Net(1, 5, 1)
        client_model_2 = Net(1, 5, 1)
        optimizer_1 = torch.optim.SGD(client_model_1.parameters(), lr=0.1)
        optimizer_2 = torch.optim.SGD(client_model_2.parameters(), lr=0.1)

        x1 = torch.unsqueeze(torch.linspace(0, 3, 10), dim=1)
        x2 = torch.unsqueeze(torch.linspace(0, 3, 10), dim=1)
        y1 = torch.exp(-x1) * torch.sin(10 * x1) + torch.rand(x1.size()) * 0.1
        y2 = torch.exp(-x2) * torch.sin(10 * x2) + torch.rand(x2.size()) * 0.1
        x1, y1, x2, y2 = Variable(x1), Variable(y1), Variable(x2), Variable(y2)

        global_model_fake = OrderedDict({'test': torch.tensor([2.0, 2.0, 2.0, 2.0, 2.0])})
        client_model_fake_1 = OrderedDict({'test': torch.tensor([1.0, 1.0, 1.0, 1.0, 1.0])})
        client_model_fake_2 = OrderedDict({'test': torch.tensor([1.0, 1.0, 1.0, 1.0, 1.0])})


        patameter_kits = parser_cfg('adaptive.yaml')
        assert patameter_kits is not None
        state = patameter_kits['state']
        params = patameter_kits['params']
        optimizer_type = {"adam": Adam, "adadelta": Adadelta, "adagrad": Adagrad, "sgd": SGD}
        self.optimizer_name = params.get('opt_name', None)
        optimizer = optimizer_type.get(self.optimizer_name, None)
        self.criterion = MSELoss()
        self.server_opt = AdapParameterServer(init_model=global_model.state_dict(), state=state, params=params,
                                              optimizer=optimizer)
        self.server_opt_fate = AdapParameterServer(init_model=global_model_fake, state=state, params=params,
                                              optimizer=optimizer)
        self.optimizer_list = [optimizer_1, optimizer_2]
        self.model_list = [client_model_1, client_model_2]
        self.model_list_fake = [client_model_fake_1, client_model_fake_2]
        self.input = [x1, x2]
        self.target = [y1, y2]
        self.round = 10

    def test_push_pop(self):
        test = OrderedDict({'t': torch.Tensor([1])})
        self.server_opt.push_client(test)
        assert len(self.server_opt.model_queue) == 1
        self.server_opt.pop_client()
        assert len(self.server_opt.model_queue) == 0

    #测试训练过程正常运行
    def test_train_pass(self):
        for i in range(self.round):
            for idx in range(len(self.model_list)):
                self.model_list[idx].load_state_dict(self.server_opt.global_model)
                input_data = self.input[idx]
                target_data = self.target[idx]
                output = self.model_list[idx].forward(input_data)
                loss = self.criterion(output, target_data)
                self.optimizer_list[idx].zero_grad()
                loss.backward()
                self.optimizer_list[idx].step()
                self.server_opt.push_client(self.model_list[idx].state_dict())
            self.server_opt.aggregation()
            assert len(self.server_opt.model_queue) == 0
            assert self.server_opt.iteration == i+1

    # 单独测试聚合过程是否正常运行
    def test_aggregation(self):
        [self.server_opt_fate.push_client(i) for i in self.model_list_fake]
        self.server_opt_fate.aggregation()
        #sgd-lr=1
        if self.optimizer_name == 'sgd':
            assert (self.server_opt_fate.global_model['test'] == torch.tensor([1., 1., 1., 1., 1.])).all().item() == True
        #adam-lr=1,
        #adam这块因为原生优化器根据原始算法编写，有偏差修正过程，和论文中简化版有不同
        #需要检验得代码（自己写得部分）只有梯度生成这块，其他都是pytorch原生得，所以检查梯度计算就好
        elif self.optimizer_name == 'adam':
            assert (self.server_opt_fate.global_model['test'].grad == torch.tensor([1., 1., 1., 1., 1.])).all().item() == True
        # adagrad-lr=1
        elif self.optimizer_name == 'adagrad':
            assert (self.server_opt_fate.global_model['test'] == torch.tensor([1., 1., 1., 1., 1.])).all().item() == True
#传github
#调研自动调参
#读论文
if __name__ == "__main__":
    unittest.main()