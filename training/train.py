import time

import jax
import jax.numpy as jnp
import numpy as np
import optax
import pandas as pd
import tensorflow as tf
import tensorflow_io as tfio  # noqa
from flax import nnx
from flax.nnx import rnglib
from jax.experimental import mesh_utils 
from jax.sharding import Mesh, NamedSharding
from jax.sharding import PartitionSpec as P
from jaxtyping import Array, Float
from jimm.models.clip import CLIP

tf.config.set_visible_devices([], "GPU")

PER_DEVICE_BATCH_SIZE = 16
GLOBAL_BATCH_SIZE = PER_DEVICE_BATCH_SIZE * jax.device_count()
NUM_EPOCHS = 3
LEARNING_RATE = 1e-4
IMAGE_SIZE = 336
HF_MODEL_NAME = "geolocal/StreetCLIP"
mesh = None


def preprocess_images(images: Array) -> Float[Array, "batch height width channels"]:
    """Preprocess images to [-1, 1] range.

    Args:
        images (Array): Raw image array

    Returns:
        Float[Array, "batch height width channels"]: Normalized images
    """
    if images.shape[-1] != 3:
        images = np.transpose(images, (0, 2, 3, 1))
    return (images.astype("float32") / 255.0) * 2.0 - 1.0


class ImageEmbeddingLookup:
    """Loads image embeddings from CSV with image path matching."""

    def __init__(self, csv_path: str):
        """
        Args:
            csv_path (str): Path to CSV with image_path,embedding columns
        """
        import ast

        df = pd.read_csv(csv_path)
        self.image_paths = df["image_path"].values
        embeddings = []
        for emb_str in df["embedding"]:
            embeddings.append(ast.literal_eval(emb_str))
        self.embeddings = jnp.array(np.stack(embeddings))

    def get_embedding(self, image_path: str) -> Float[Array, " embedding_dim"]:
        """
        Args:
            image_path (str): Path to image file

        Returns:
            Float[Array, "embedding_dim"]: Image embedding
        """
        path_idx = jnp.where(self.image_paths == image_path)[0]
        return self.embeddings[path_idx[0]]


class VisionLocationModel(nnx.Module):
    """Vision-location contrastive model with frozen CLIP and trainable projection."""

    def __init__(
        self,
        clip_model_path: str,
        image_embedding_csv: str,
        projection_dim: int = 512,
        rngs: rnglib.Rngs = nnx.Rngs(0),
    ):
        """
        Args:
            clip_model_path (str): Path to pretrained CLIP model
            image_embedding_csv (str): Path to image embeddings CSV
            projection_dim (int): Dimension of projection layer
            rngs (rnglib.Rngs): Random number generator
        """
        self.clip = CLIP.from_pretrained(clip_model_path, use_pytorch=True, param_dtype=jnp.bfloat16, dtype=jnp.bfloat16, rngs=rngs)
        self.image_lookup = ImageEmbeddingLookup(image_embedding_csv)

        vision_dim = self.clip.vision_width
        embedding_dim = self.image_lookup.embeddings.shape[1]

        self.vision_projection = nnx.Linear(vision_dim, projection_dim, rngs=rngs)
        self.embedding_projection = nnx.Linear(embedding_dim, projection_dim, rngs=rngs)

    def encode_vision(self, images: Float[Array, "batch height width channels"]) -> Float[Array, "batch projection_dim"]:
        """
        Args:
            images (Float[Array, "batch height width channels"]): Input images

        Returns:
            Float[Array, "batch projection_dim"]: Vision features
        """
        vision_features = self.clip.vision_model(images)
        return self.vision_projection(vision_features)

    def encode_embedding(self, image_paths: list[str]) -> Float[Array, "batch projection_dim"]:
        """
        Args:
            image_paths (list[str]): List of image paths

        Returns:
            Float[Array, "batch projection_dim"]: Embedding features
        """
        embeddings = jnp.stack([self.image_lookup.get_embedding(path) for path in image_paths])
        return self.embedding_projection(embeddings)

    def __call__(
        self,
        images: Float[Array, "batch height width channels"],
        embeddings: Float[Array, "batch embedding_dim"],
    ) -> Float[Array, "batch batch"]:
        """
        Args:
            images (Float[Array, "batch height width channels"]): Input images
            embeddings (Float[Array, "batch embedding_dim"]): Precomputed embeddings

        Returns:
            Float[Array, "batch batch"]: Similarity matrix
        """
        vision_features = self.encode_vision(images)
        embedding_features = self.embedding_projection(embeddings)

        vision_features = vision_features / jnp.linalg.norm(vision_features, axis=-1, keepdims=True)
        embedding_features = embedding_features / jnp.linalg.norm(embedding_features, axis=-1, keepdims=True)

        return vision_features @ embedding_features.T


def contrastive_loss(logits: Float[Array, "batch batch"]) -> Float[Array, ""]:
    """
    Args:
        logits (Float[Array, "batch batch"]): Similarity matrix

    Returns:
        Float[Array, ""]: Contrastive loss
    """
    batch_size = logits.shape[0]
    labels = jnp.arange(batch_size)

    vision_loss = optax.softmax_cross_entropy_with_integer_labels(logits, labels)
    location_loss = optax.softmax_cross_entropy_with_integer_labels(logits.T, labels)

    return (vision_loss.mean() + location_loss.mean()) / 2


def compute_loss_and_metrics(
    model: VisionLocationModel,
    images: Float[Array, "batch height width channels"],
    embeddings: Float[Array, "batch embedding_dim"],
) -> tuple[Float[Array, ""], dict[str, Float[Array, ""]]]:
    """Compute loss and accuracy metrics.

    Args:
        model (VisionLocationModel): Vision-location model
        images (Float[Array, "batch height width channels"]): Batch of images
        embeddings (Float[Array, "batch embedding_dim"]): Precomputed embeddings

    Returns:
        Tuple[Float[Array, ""], Dict[str, Float[Array, ""]]]: Loss and metrics dictionary
    """
    logits = model(images, embeddings)
    loss = contrastive_loss(logits)
    predictions = jnp.argmax(logits, axis=-1)
    labels = jnp.arange(images.shape[0])
    accuracy = jnp.mean(predictions == labels)
    return loss, {"accuracy": accuracy}


def train_step_impl(
    model: VisionLocationModel,
    optimizer: nnx.Optimizer,
    images: Float[Array, "batch height width channels"],
    embeddings: Float[Array, "batch embedding_dim"],
) -> tuple[Float[Array, ""], dict[str, Float[Array, ""]]]:
    """Training step implementation.

    Args:
        model (VisionLocationModel): Vision-location model
        optimizer (nnx.Optimizer): NNX optimizer
        images (Float[Array, "batch height width channels"]): Batch of images
        embeddings (Float[Array, "batch embedding_dim"]): Precomputed embeddings

    Returns:
        Tuple[Float[Array, ""], Dict[str, Float[Array, ""]]]: Loss and metrics
    """
    trainable_params = nnx.All(nnx.Param, nnx.Any(nnx.PathContains("vision_projection"), nnx.PathContains("embedding_projection")))

    diff_state = nnx.DiffState(0, trainable_params)
    grad_fn = nnx.value_and_grad(compute_loss_and_metrics, has_aux=True, argnums=diff_state)
    (loss, metrics), grads = grad_fn(model, images, embeddings)
    optimizer.update(grads)
    return loss, metrics


def create_dataset_from_csv(csv_path: str) -> tf.data.Dataset:
    """Create dataset from CSV with image_path and embedding columns, using pandarallel preprocessing.

    Args:
        csv_path (str): Path to CSV file

    Returns:
        tf.data.Dataset: Dataset with pre-processed images and embeddings as numpy arrays
    """
    import ast
    from pandarallel import pandarallel

    pandarallel.initialize(progress_bar=True)

    df = pd.read_csv(csv_path)

    def preprocess_row(row):
        """Preprocess a single row with image loading and embedding parsing."""
        image_path = row["image_path"]
        image = tf.io.read_file(image_path)
        image = tf.image.decode_image(image, channels=3)
        image = tf.image.resize(image, [IMAGE_SIZE, IMAGE_SIZE])
        image = tf.cast(image, tf.uint8)
        image_np = preprocess_images(image.numpy())

        embedding = np.array(ast.literal_eval(row["embedding"]), dtype=np.float32)

        return {"image": image_np, "embedding": embedding}

    processed_data = df.parallel_apply(preprocess_row, axis=1).tolist()

    def generator():
        for data in processed_data:
            yield data

    return tf.data.Dataset.from_generator(
        generator,
        output_signature={
            "image": tf.TensorSpec(shape=(IMAGE_SIZE, IMAGE_SIZE, 3), dtype=tf.float32),
            "embedding": tf.TensorSpec(shape=(64,), dtype=tf.float32),
        },
    )


def load_and_shard_batch(batch: dict[str, tf.Tensor], mesh: Mesh) -> tuple[Float[Array, "batch height width channels"], Float[Array, "batch embedding_dim"]]:
    """Load and shard batch across devices using device_put.

    Args:
        batch (Dict[str, tf.Tensor]): TensorFlow batch dictionary with pre-processed numpy arrays
        mesh (Mesh): Device mesh

    Returns:
        Tuple[Float[Array, "batch height width channels"], Float[Array, "batch embedding_dim"]]: Sharded JAX arrays
    """
    # Convert TensorFlow tensors to numpy arrays (already pre-processed)
    images = batch["image"].numpy()
    embeddings = batch["embedding"].numpy()

    # Create sharding specifications
    image_sharding = NamedSharding(mesh, P("model", None, None, None))
    embedding_sharding = NamedSharding(mesh, P("model", None))

    # Use device_put to distribute arrays across devices
    global_images = jax.device_put(images, image_sharding)
    global_embeddings = jax.device_put(embeddings, embedding_sharding)

    return global_images, global_embeddings


@nnx.jit(static_argnums=(0,))
def create_sharded_model_and_optimizer(
    image_embedding_csv: str,
) -> tuple[VisionLocationModel, nnx.Optimizer]:
    """Create and shard the vision-location model and optimizer.

    Args:
        image_embedding_csv (str): Path to image embeddings CSV file

    Returns:
        Tuple[VisionLocationModel, nnx.Optimizer]: Sharded model and optimizer
    """
    model = VisionLocationModel(
        clip_model_path=HF_MODEL_NAME,
        image_embedding_csv=image_embedding_csv,
        projection_dim=512,
        rngs=nnx.Rngs(0),
    )
    state = nnx.state(model)
    pspecs = nnx.get_partition_spec(state)
    sharded_state = jax.lax.with_sharding_constraint(state, pspecs)
    nnx.update(model, sharded_state)

    trainable_params = nnx.All(nnx.Param, nnx.Any(nnx.PathContains("vision_projection"), nnx.PathContains("embedding_projection")))

    optimizer = nnx.Optimizer(model, optax.adam(LEARNING_RATE), wrt=trainable_params)
    state = nnx.state(optimizer)
    pspecs = nnx.get_partition_spec(state)
    sharded_state = jax.lax.with_sharding_constraint(state, pspecs)
    nnx.update(optimizer, sharded_state)
    return model, optimizer


def main() -> None:
    """Main training function."""
    global mesh
    devices = mesh_utils.create_device_mesh((jax.device_count(),))
    mesh = Mesh(devices, ("model",))

    with mesh:
        model, optimizer = create_sharded_model_and_optimizer("/home/supersketchy/nfs_share/deeper-seek/path_lat_lon_with_embeddings_test.csv")

    model_spec = nnx.get_partition_spec(model)
    optimizer_spec = nnx.get_partition_spec(optimizer)
    image_sharding = NamedSharding(mesh, P("model", None, None, None))
    embedding_sharding = NamedSharding(mesh, P("model", None))

    train_step = nnx.jit(
        train_step_impl,
        in_shardings=(model_spec, optimizer_spec, image_sharding, embedding_sharding),
    )

    train_dataset_raw = create_dataset_from_csv("/home/supersketchy/nfs_share/deeper-seek/path_lat_lon_with_embeddings_test.csv")
    train_dataset = train_dataset_raw.repeat(NUM_EPOCHS).batch(GLOBAL_BATCH_SIZE, drop_remainder=True).prefetch(tf.data.AUTOTUNE)

    model.train()
    train_iterator = train_dataset.as_numpy_iterator()

    for step, batch in enumerate(train_iterator):
        start_time = time.time()
        images, embeddings = load_and_shard_batch(batch, mesh)
        loss, metrics = train_step(model, optimizer, images, embeddings)

        if jax.process_index() == 0:
            step_time = time.time() - start_time
            print(f"Step {step + 1}: Loss={loss}, Acc={metrics['accuracy']}, Time={step_time}s")


if __name__ == "__main__":
    main()
