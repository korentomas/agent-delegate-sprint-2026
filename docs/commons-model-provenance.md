# Models used in the shared-library experiment

All artifacts are text-only GGUF inference at Q4_K_M. The vision projectors are not loaded. Files were obtained from the listed public repositories at pinned commits and checked against their published LFS SHA256; the existing standard Qwen file was rehashed before the new study. We use these public derivatives as exploratory comparisons, without training or modifying weights ourselves.

| Label | Artifact source | Selected lineage |
|---|---|---|
| Qwen standard | https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF | Qwen/Qwen3-4B-Instruct-2507 |
| Qwen abliterated | https://huggingface.co/prithivMLmods/Qwen3-4B-2507-abliterated-GGUF | Selected **Instruct** subdirectory/file; repository also distributes a separate Thinking derivative. The card lists Huihui Instruct and Thinking parents. |
| Gemma standard | https://huggingface.co/unsloth/gemma-3-4b-it-GGUF | google/gemma-3-4b-it |
| Gemma abliterated | https://huggingface.co/mlabonne/gemma-3-4b-it-abliterated-v2-GGUF | mlabonne/gemma-3-4b-it-abliterated-v2, derived from google/gemma-3-4b-it |

Full commit IDs, filenames, sizes, weight hashes and repository-reported licenses are in `data/commons-model-*.json`. Qwen repositories report Apache-2.0; Gemma repositories report the Gemma license. Model weights are not redistributed with the experiment. Inference uses the existing local llama.cpp HIP engine; `server_properties.json` in each run records its build string, default sampling configuration, model identity and exact chat template. The client request records temperature 0.5, seeds, output budget and the schema on every call. Prompted points or priorities do not update model weights.

Same quantization format does not mean identical quantization provenance. Derivatives may change general competence, output validity, instruction following and reporting tendencies in addition to refusal behavior. There is no matched unmodified conversion of the exact same intermediate tensors, nor a manipulation check establishing an isolated refusal change. Report differences as differences between these artifacts; do not attribute them exclusively to abliteration or treat any model as inherently deceptive.

The shared machine retains its normal 27B server. Experimental 4B servers are limited to local loopback ports and run in scheduled batches to reduce memory pressure. Concurrent GPU execution and different tokenizers make wall-clock time and token counts imperfectly comparable across families. Coordinator cost comparisons within a model are more directly interpretable, but episode reports determine how often a coordinator is called.

## Separate standard 27B screen

The fresh-input screen uses `unsloth/Qwen3.8-27B-GGUF` at revision `f1bfb127c64f7072bdd2cad55f258b9c8b2910fe`, file `Qwen3.8-27B-UD-Q4_K_XL.gguf`. Its local SHA256 was recomputed and matched the repository's `x-linked-etag` on September 12: `bee238bbeb3dc0a34bde4d0dedbaee1f98c009e8bb4226f03070054c12fb1372`. The card identifies Qwen/Qwen3.8-27B and Apache-2.0. This standard, non-abliterated artifact ran with upstream llama.cpp, no MTP/speculation and thinking disabled, on a separate loopback test server subsequently stopped. The user's ordinary FP4 server was not reconfigured. Metadata and all server/request settings accompany the screen records. The 2+3 FP4 preflight remains separate from scored results.
