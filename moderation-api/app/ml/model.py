import torch
import torch.nn as nn


class MultiHeadBiLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers, dropout, max_len):
        super().__init__()
        self.max_len = max_len
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.bilstm = nn.LSTM(
            embed_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        lstm_out_dim = hidden_dim * 2

        self.head_hate = nn.Sequential(
            nn.Linear(lstm_out_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 3),
        )
        self.head_spam = nn.Sequential(
            nn.Linear(lstm_out_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 1),
        )
        self.head_jigsaw = nn.Sequential(
            nn.Linear(lstm_out_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 1),
        )

    def forward(self, input_ids):
        emb = self.embedding(input_ids)
        lstm_out, _ = self.bilstm(emb)
        pooled = lstm_out.mean(dim=1)
        hate_out = self.head_hate(pooled)
        spam_out = self.head_spam(pooled)
        jigsaw_out = self.head_jigsaw(pooled)
        return hate_out, spam_out, jigsaw_out
