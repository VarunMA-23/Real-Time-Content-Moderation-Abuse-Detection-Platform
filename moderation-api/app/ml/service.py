import json
import os
import pickle
import time
import torch

from app.ml.model import MultiHeadBiLSTM

_MODEL_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "ML_models_API", "ML_files")
)


class ModelService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._model = None
            cls._instance._vocab = None
            cls._instance._config = None
        return cls._instance

    def _load(self):
        if self._model is not None:
            return

        config_path = os.path.join(_MODEL_DIR, "model_config.json")
        with open(config_path) as f:
            self._config = json.load(f)

        vocab_path = os.path.join(_MODEL_DIR, "word2idx.pkl")
        with open(vocab_path, "rb") as f:
            self._vocab = pickle.load(f)

        ckpt_path = os.path.join(_MODEL_DIR, "multihead_bilstm_full.pt")
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)

        model = MultiHeadBiLSTM(
            vocab_size=self._config["vocab_size"],
            embed_dim=self._config["embed_dim"],
            hidden_dim=self._config["hidden_dim"],
            num_layers=self._config["num_layers"],
            dropout=self._config["dropout"],
            max_len=self._config["max_len"],
        )
        model.load_state_dict(ckpt["model_state"])
        model.eval()
        self._model = model

    def predict(self, text: str) -> dict:
        self._load()
        max_len = self._config["max_len"]
        tokens = text.lower().split()
        ids = [self._vocab.get(t, self._vocab["<UNK>"]) for t in tokens[:max_len]]
        if len(ids) < max_len:
            ids += [self._vocab["<PAD>"]] * (max_len - len(ids))

        input_ids = torch.tensor([ids], dtype=torch.long)

        with torch.no_grad():
            hate_out, spam_out, jigsaw_out = self._model(input_ids)

        hate_probs = torch.softmax(hate_out, dim=1)
        toxicity = float(hate_probs[0, 0])
        spam = float(torch.sigmoid(spam_out[0, 0]))
        self_harm = float(torch.sigmoid(jigsaw_out[0, 0]))

        return {
            "toxicity": round(toxicity, 4),
            "spam": round(spam, 4),
            "selfHarm": round(self_harm, 4),
        }

    def predict_with_latency(self, text: str) -> tuple:
        start = time.perf_counter()
        scores = self.predict(text)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return scores, latency_ms
