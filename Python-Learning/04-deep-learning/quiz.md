# Phase 4: Deep Learning - Quiz

A comprehensive quiz covering all 7 modules of the Deep Learning phase.

**Total Questions: 25**
- Easy: 8 questions
- Medium: 10 questions
- Hard: 7 questions

---

## Easy Questions (1-8)

**1. What is the purpose of the backward() method in PyTorch?**
- A) To move the model to a device
- B) To compute gradients during backpropagation
- C) To save model checkpoints
- D) To load pre-trained weights

**2. Which loss function is typically used for multi-class classification?**
- A) MSELoss
- B) BCEWithLogitsLoss
- C) CrossEntropyLoss
- D) L1Loss

**3. What does the optimizer.zero_grad() method do?**
- A) Resets the model weights
- B) Clears accumulated gradients
- C) Updates model parameters
- D) Computes new gradients

**4. In a convolution operation, what does the stride parameter control?**
- A) The size of the output
- B) How many pixels the kernel moves at each step
- C) The number of filters
- D) The depth of the network

**5. What is the main advantage of using pre-trained models in transfer learning?**
- A) They are always more accurate
- B) They require less training data and time
- C) They eliminate the need for labeled data
- D) They work on any dataset without modification

**6. What is the purpose of data augmentation?**
- A) To increase the number of training samples artificially
- B) To improve computational efficiency
- C) To replace labeled data
- D) To make the model more complex

**7. Which of the following is NOT a component of a transformer?**
- A) Multi-head attention
- B) Feed-forward network
- C) Positional encoding
- D) Convolutional layer

**8. What does a tokenizer do in the context of NLP?**
- A) Creates embeddings for text
- B) Converts text into tokens that the model can process
- C) Trains the language model
- D) Evaluates model performance

---

## Medium Questions (9-18)

**9. What is the key difference between feature extraction and fine-tuning in transfer learning?**
- A) Feature extraction freezes the backbone while fine-tuning trains it
- B) They are the same thing with different names
- C) Fine-tuning only works with small datasets
- D) Feature extraction is faster but fine-tuning is more accurate

**10. In a ResNet block, what is the purpose of the skip connection?**
- A) To reduce computational cost
- B) To allow gradients to flow directly through and ease training of very deep networks
- C) To increase the number of parameters
- D) To reduce the spatial dimensions

**11. What does attention weight softmax produce?**
- A) A probability distribution over input elements
- B) A fixed value between -1 and 1
- C) A gradient for backpropagation
- D) A one-hot encoded vector

**12. In the scaled dot-product attention formula, why is the dot product divided by sqrt(d_k)?**
- A) To prevent exploding gradients in the softmax
- B) To increase model capacity
- C) To reduce memory usage
- D) To make computations faster

**13. What is the relationship between pooling and spatial dimensionality?**
- A) Pooling increases spatial dimensions
- B) Pooling reduces spatial dimensions while preserving important features
- C) Pooling has no effect on spatial dimensions
- D) Pooling replaces spatial dimensions with channel dimensions

**14. In the pipeline API from Hugging Face, what does the text-generation pipeline do?**
- A) Classifies text into categories
- B) Summarizes long texts
- C) Generates new text continuations based on a prompt
- D) Extracts entities from text

**15. What is the purpose of learning rate scheduling?**
- A) To keep the learning rate constant throughout training
- B) To adjust the learning rate during training for better convergence
- C) To eliminate the need for optimization
- D) To replace the optimizer entirely

**16. How does batch normalization affect training?**
- A) It slows down training
- B) It stabilizes training and allows higher learning rates
- C) It removes the need for activation functions
- D) It increases overfitting

**17. In multi-head attention, why do we split into multiple heads?**
- A) To reduce model parameters
- B) To allow the model to attend to different representation subspaces in parallel
- C) To make the model smaller
- D) To replace the need for multiple layers

**18. What is the primary purpose of the Hugging Face Hub?**
- A) A centralized repository for pre-trained models, datasets, and spaces
- B) A dataset annotation platform
- C) A GPU provider
- D) A code version control system

---

## Hard Questions (19-25)

**19. Explain the role of positional encoding in transformers and why it's necessary.**

The positional encoding provides information about token positions in the sequence using sinusoidal functions. Since the transformer's attention mechanism is position-agnostic, positional encoding must be added to give the model information about token order and relative distances.

**20. What is gradient clipping and in which scenarios is it particularly important?**

Gradient clipping limits the magnitude of gradients before the optimizer step. It's critical in RNNs and LSTMs to prevent exploding gradients, which can cause training instability. It's also important in transformers with very deep networks.

**21. Describe the differences between encoder-only, decoder-only, and encoder-decoder architectures. Give an example of each.**

- **Encoder-only**: BERT - performs bidirectional encoding, good for classification
- **Decoder-only**: GPT-2, GPT-3 - generates text autoregressively, can't see future tokens
- **Encoder-decoder**: T5, BART - encodes input then decodes output, good for seq2seq tasks like translation

**22. In transfer learning, why do we typically use different learning rates for the backbone and head?**

The backbone contains pre-trained features that are already useful, so we want to fine-tune them slowly with a small learning rate. The head is randomly initialized and needs to be trained more aggressively with a higher learning rate. This balances preserving learned features with adapting to the new task.

**23. How does layer normalization in transformers differ from batch normalization in CNNs, and why is it better suited for transformers?**

Batch normalization normalizes across the batch dimension, making it dependent on batch size and problematic during inference. Layer normalization normalizes across the feature dimension, making it independent of batch size and more suitable for variable-length sequences in transformers.

**24. Explain the mechanism of self-attention and how it relates to the "attention is all you need" concept.**

Self-attention allows each token to dynamically compute relevance scores to all other tokens, creating a fully connected graph of dependencies. Unlike RNNs' sequential processing, self-attention processes all tokens in parallel, capturing both distant and close dependencies. This parallelization and effectiveness led to transformers replacing RNNs in many NLP tasks.

**25. Design a training pipeline for a large language model that incorporates: (1) mixed precision training, (2) gradient accumulation, (3) learning rate scheduling, and (4) evaluation on validation set.**

A comprehensive pipeline would:
1. Use `torch.cuda.amp.autocast()` for mixed precision computation
2. Accumulate gradients over multiple batches using `loss = loss / accumulation_steps` before backward()
3. Implement `OneCycleLR` or `CosineAnnealingLR` scheduler
4. Evaluate on validation set every N batches using a separate forward pass without gradient computation
5. Save best checkpoint based on validation loss
6. Use distributed training with `torch.nn.parallel.DistributedDataParallel` for multi-GPU
7. Log metrics to TensorBoard for monitoring

---

## Answer Key

### Easy Answers
1. **B** - backward() computes gradients via backpropagation
2. **C** - CrossEntropyLoss for multi-class classification
3. **B** - zero_grad() clears accumulated gradients
4. **B** - stride controls how far the kernel moves
5. **B** - Pre-trained models reduce training time and data requirements
6. **A** - Augmentation artificially increases training data
7. **D** - Transformers don't use convolutional layers (though some variants do)
8. **B** - Tokenizers convert text to tokens

### Medium Answers
9. **A** - Feature extraction freezes backbone, fine-tuning trains it
10. **B** - Skip connections ease gradient flow in deep networks
11. **A** - Softmax produces probability distributions
12. **A** - Division by sqrt(d_k) prevents exploding gradients
13. **B** - Pooling reduces spatial dimensions
14. **C** - text-generation generates text continuations
15. **B** - Learning rate scheduling adjusts LR during training
16. **B** - Batch normalization stabilizes training
17. **B** - Multiple heads allow parallel attention to different subspaces
18. **A** - Hub is a central repository for models and datasets

### Hard Answers
19-25. See explanations in the questions above

---

## Study Tips

- Focus on understanding why techniques work, not just how
- Practice implementing concepts in code
- Run the provided exercise solutions and modify them
- Build small projects combining multiple concepts
- Reference the lesson materials when unsure
