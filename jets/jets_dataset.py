import torch
from torch.utils.data import Dataset


class JetsDataset(Dataset):
    def __init__(self, args):
        mask = '_mask' if args.mask else ''
        dataset = torch.load(args.dataset_path + 'all_' + args.jets + '_jets_' + str(args.num_hits) + 'p_' + args.coords + mask + '.pt').float()
        jet_features = torch.load(args.dataset_path + 'all_' + args.jets + '_jets_' + str(args.num_hits) + 'p_jetptetamass.pt').float()[:, :args.clabels]

        if args.coords == 'cartesian':
            args.maxp = float(torch.max(torch.abs(dataset)))
            dataset = dataset / args.maxp

            cutoff = int(dataset.size(0) * args.ttsplit)

            if(args.train):
                self.X = dataset[:cutoff]
            else:
                self.X = dataset[cutoff:]
        elif args.coords == 'polarrel' or args.coords == 'polarrelabspt':
            args.maxepp = [float(torch.max(torch.abs(dataset[:, :, i]))) for i in range(3)]
            print(args.maxepp)
            for i in range(3):
                dataset[:, :, i] /= args.maxepp[i]

            dataset[:, :, 2] -= 0.5
            # dataset[:, :, 2] *= 2
            dataset *= args.norm
            self.X = dataset

        if args.clabels == 1:
            args.maxjf = [torch.max(torch.abs(jet_features))]
            jet_features /= args.maxjf[0]
        else:
            [float(torch.max(torch.abs(jet_features[:, :, i]))) for i in range(args.clabels)]
            for i in range(args.clabels):
                jet_features[:, i] /= args.maxjf[i]

        self.jet_features = jet_features * args.norm

        print(self.jet_features)

        print("Dataset loaded")
        print(self.X.shape)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.jet_features[idx]
