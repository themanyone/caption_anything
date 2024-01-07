#!/usr/bin/env python
## init_whisper_jax
##
## A whisper_jax that operates on numpy.ndarray instead of audio files
##
## from https://github.com/sanchit-gandhi/whisper-jax/tree/main/app
## If you want a server, use the above.
## This is a stripped-down, importable version, without multiprocessing
## And without batching, which only slows it down when run as an app.
import logging
import math
from whisper_jax import FlaxWhisperPipline
import jax.numpy as jnp
import numpy as np
import time
from transformers.pipelines.audio_utils import ffmpeg_read
# from multiprocessing import Pool

task = "transcribe"
return_timestamps = False
checkpoint = "openai/whisper-small.en"
BATCH_SIZE = 1
CHUNK_LENGTH_S = 30
# NUM_PROC = 8

logger = logging.getLogger("jax_trans2")
logger.setLevel(logging.INFO)

def identity(batch):
    return batch

# Instantiate the pipeline
pipeline = None
step = 0

def tqdm_generate(inputs: dict, task: str, return_timestamps: bool):
    inputs_len = inputs["array"].shape[0]
    all_chunk_start_idx = np.arange(0, inputs_len, step)
    num_samples = len(all_chunk_start_idx)
    num_batches = math.ceil(num_samples / BATCH_SIZE)
    dummy_batches = list(
        range(num_batches)
    )

    dataloader = pipeline.preprocess_batch(inputs, chunk_length_s=CHUNK_LENGTH_S, batch_size=BATCH_SIZE)
    logger.info("pre-processing audio file...")
    # dataloader = pool.map(identity, dataloader)
    dataloader = list(map(identity, dataloader))  # Use list() to convert map object to a list
    logger.info("done pre-processing")

    model_outputs = []
    start_time = time.time()
    logger.info(task)
    # iterate over our chunked audio samples - always predict timestamps to reduce hallucinations
    for batch, _ in zip(dataloader, dummy_batches):
        model_outputs.append(pipeline.forward(batch, batch_size=BATCH_SIZE, task=task, return_timestamps=return_timestamps))
    runtime = time.time() - start_time
    logger.info("done " + task)

    logger.info("post-processing...")
    post_processed = pipeline.postprocess(model_outputs, return_timestamps=return_timestamps)
    text = post_processed["text"]
    if return_timestamps:
        timestamps = post_processed.get("chunks")
        timestamps = [
            f"[{format_timestamp(chunk['timestamp'][0])} -> {format_timestamp(chunk['timestamp'][1])}] {chunk['text']}"
            for chunk in timestamps
        ]
        text = "\n".join(str(feature) for feature in timestamps)
    logger.info("done post-processing")
    return text, runtime

def init_pipeline():
    global step
    global pipeline
    pipeline = FlaxWhisperPipline(checkpoint, dtype=jnp.bfloat16, batch_size=BATCH_SIZE)
    stride_length_s = CHUNK_LENGTH_S / 6
    chunk_len = round(CHUNK_LENGTH_S * pipeline.feature_extractor.sampling_rate)
    stride_left = stride_right = round(stride_length_s * pipeline.feature_extractor.sampling_rate)
    step = chunk_len - stride_left - stride_right
    # pool = Pool(NUM_PROC)
    logger.info("compiling forward call...")
    start = time.time()
    random_inputs = {"input_features": np.ones((BATCH_SIZE, 80, 3000))}
    random_timestamps = pipeline.forward(random_inputs, batch_size=BATCH_SIZE, return_timestamps=return_timestamps)
    compile_time = time.time() - start
    logger.info(f"compiled in {compile_time}s")

if __name__ == "__main__":
    # Example usage
    init_pipeline()
    # Load the audio file
    with open("out.wav", "rb") as f:
        inputs = f.read()
    # ffmpeg_read also converts inputs to the required type numpy.ndarray
    inputs = ffmpeg_read(inputs, pipeline.feature_extractor.sampling_rate)
    inputs = {"array": inputs, "sampling_rate": pipeline.feature_extractor.sampling_rate}
    logger.info("done loading")
    text, runtime = tqdm_generate(inputs, task=task, return_timestamps=return_timestamps)
    print(text, runtime)