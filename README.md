# FractureCoT — SFT / GRPO 权重归档

本仓库为 hangcao87 的公开模型归档，仅发布一份初始 SFT 和一份已评测 GRPO。权重文件在 [Releases → weights-20261101 → Assets](https://github.com/hangcao87/fracturecot-sft-grpo-weights/releases/tag/weights-20261101)，普通 `git clone` 只下载清单、恢复脚本和说明。

## 两组权重

| 目录 | 内容 | 原始文件总大小 | 使用方法 |
|---|---|---:|---|
| `initial_sft` | 早期小样本 SFT 的 PEFT 语言 LoRA 适配器及配置 | 193,199,757 bytes | 配合对应 Qwen3.5-9B 基座加载 |
| `grpo` | 作者指定且已经评测的 GRPO 合并模型 | 18,839,793,193 bytes | 可作为完整 Transformers 模型目录加载 |

初始 SFT 对应 `paper_pipeline_v5_20261012/sft_full/final_adapter`。GRPO 对应服务器 `/root/Qwen3.5-9B-merged`。初始 SFT 的适配器权重及 GRPO 的全部 12 个源文件均与既有评测清单核对；其余 SFT 配套文件按原目录归档并记录哈希。此次上传没有重新训练、合并或推理，也不改变既有实验结论。GRPO 标签沿用作者指定的检查点身份；文件哈希证明交付文件一致，不单独证明训练血缘或最优性。

## 下载与恢复

仓库和 Release 已公开。浏览器可匿名下载，无需申请访问权限。使用 GitHub CLI 的用户可执行：

```bash
gh repo clone hangcao87/fracturecot-sft-grpo-weights
cd fracturecot-sft-grpo-weights
gh release download weights-20261101 --repo hangcao87/fracturecot-sft-grpo-weights --dir assets
python3 restore_weights.py --assets assets --output weights
```

脚本逐片校验 SHA256、按顺序恢复 `.safetensors`，然后校验每个原始文件的大小和 SHA256。仅恢复 SFT 可加 `--model initial_sft`；仅恢复 GRPO 可加 `--model grpo`。全部恢复需至少约 40 GB 空闲磁盘用于下载分片和重建模型。脚本不会覆盖已有不同内容的模型文件。

每个大权重分片最多 1 GiB；分片只是传输格式，不是可直接加载的模型分片。先运行恢复脚本。

## 加载提示

- **GRPO：** 模型类为 `Qwen3_5ForConditionalGeneration`，目录 `weights/grpo`。使用支持 Qwen3.5 的 Transformers 版本，并加载同目录的处理器与原始聊天模板。
- **SFT：** 先加载对应的 Qwen3.5-9B 基座，再用 PEFT 从 `weights/initial_sft` 加载适配器。原始 `adapter_config.json` 保留服务器上的基座路径；在其他机器上显式提供本机基座路径，不要直接依赖该绝对路径。
- SFT 适配器仅 173,188,512 bytes，包含 496 个语言 LoRA 张量；保存范围为语言 LoRA，需配合对应 9B 基座使用。
- 使用训练/评测一致的提示词、坐标合同、图像预处理、生成参数及停止符；不同推理配置不能直接用于重现原指标。
- `training_args.bin` 是原始归档文件，不需要加载它来推理；不要对不可信的 pickle 文件调用反序列化。

## 校验与许可

`release_manifest.json` 记录所有原始文件与传输分片的大小和 SHA256，`SHA256SUMS` 用于快速校验下载资产，`source_verification.json` 记录此次来源核验。权重不包含原始患者影像、训练数据、密码或访问令牌。

`BASE_MODEL_LICENSE` 保留源基座附带的 Apache-2.0 许可证。模型是研究归档；本仓库不授予基础模型和源材料许可之外的额外权利。对外再分发前核对相应许可与研究授权。
