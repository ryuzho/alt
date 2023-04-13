import argparse
from torch.utils.data import DataLoader
import pytorch_lightning as pl
import wandb
from pytorch_lightning.loggers import WandbLogger
from ray.tune.integration.pytorch_lightning import TuneReportCallback

from evaluation.evaluation import compute_sequence_accuracy, compute_sequence_cross_entropy
from model.trans_generator import SmilesGenerator
from train_generator import BaseGeneratorLightningModule
from data.dataset import K2TreeDataset


class SmilesGeneratorLightningModule(BaseGeneratorLightningModule):
    def __init__(self, hparams):
        super().__init__(hparams)

    def setup_model(self, hparams):
        self.model = SmilesGenerator(
            num_layers=hparams.num_layers,
            emb_size=hparams.emb_size,
            nhead=hparams.nhead,
            dim_feedforward=hparams.dim_feedforward,
            input_dropout=hparams.input_dropout,
            dropout=hparams.dropout,
            max_len=hparams.max_len,
            string_type=hparams.string_type,
            tree_pos=hparams.tree_pos
        )

    ### 
    def train_dataloader(self):
        return DataLoader(
            self.train_dataset,
            batch_size=self.hparams.batch_size,
            shuffle=True,
            collate_fn=K2TreeDataset.collate_fn,
            num_workers=self.hparams.num_workers,
        )
        
    def test_dataloader(self):
        return DataLoader(
            self.test_dataset,
            batch_size=self.hparams.batch_size,
            shuffle=False,
            collate_fn=K2TreeDataset.collate_fn,
            num_workers=self.hparams.num_workers,
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_dataset,
            batch_size=self.hparams.batch_size,
            shuffle=False,
            collate_fn=K2TreeDataset.collate_fn,
            num_workers=self.hparams.num_workers,
        )

    ### Main steps
    def shared_step(self, batched_data):
        loss, statistics = 0.0, dict()
        logits = self.model(batched_data)
        loss = compute_sequence_cross_entropy(logits, batched_data, self.hparams.string_type)
        statistics["loss/total"] = loss
        # statistics["acc/total"] = compute_sequence_accuracy(logits, batched_data, ignore_index=0)[0]

        return loss, statistics

    
    @staticmethod
    def add_args(parser):
        
        parser.add_argument("--dataset_name", type=str, default="GDSS_ego")
        parser.add_argument("--batch_size", type=int, default=64)
        parser.add_argument("--num_workers", type=int, default=6)

        parser.add_argument("--order", type=str, default="C-M")
        parser.add_argument("--replicate", type=int, default=0)
        #
        parser.add_argument("--emb_size", type=int, default=512)
        parser.add_argument("--dropout", type=int, default=0.1)
        parser.add_argument("--lr", type=float, default=0.0005)
        
        parser.add_argument("--check_sample_every_n_epoch", type=int, default=5)
        parser.add_argument("--num_samples", type=int, default=1000)
        parser.add_argument("--sample_batch_size", type=int, default=100)
        parser.add_argument("--max_epochs", type=int, default=500)
        parser.add_argument("--wandb_on", type=str, default='disabled')
        
        parser.add_argument("--group", type=str, default='string')
        parser.add_argument("--model", type=str, default='trans')
        parser.add_argument("--max_len", type=int, default=272)
        parser.add_argument("--string_type", type=str, default='bfs-deg')
        
        # transformer
        parser.add_argument("--num_layers", type=int, default=3)
        parser.add_argument("--nhead", type=int, default=8)
        parser.add_argument("--dim_feedforward", type=int, default=512)
        parser.add_argument("--input_dropout", type=int, default=0.0)
        parser.add_argument("--tree_pos", action="store_true")
        parser.add_argument("--gradient_clip_val", type=float, default=1.0)

        return parser


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    SmilesGeneratorLightningModule.add_args(parser)
    hparams = parser.parse_args()
    
    wandb_logger = WandbLogger(name=f'{hparams.dataset_name}-{hparams.model}-{hparams.string_type}', 
                               project='gcg', group=f'{hparams.group}', mode=f'{hparams.wandb_on}')
    
    wandb.config.update(hparams)


    model = SmilesGeneratorLightningModule(hparams)


    trainer = pl.Trainer(
        gpus=1,
        default_root_dir="../resource/log/",
        max_epochs=hparams.max_epochs,
        gradient_clip_val=hparams.gradient_clip_val,
        logger=wandb_logger
    )
    trainer.fit(model)