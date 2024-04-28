import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, AdamW
# import numpy as np
# import pandas as pd
# from sklearn.model_selection import train_test_split
# from torch.utils.data import TensorDataset, DataLoader, RandomSampler
# from torch.optim import AdamW as TorchAdamW
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# # Read data from CSV file
# data = pd.read_csv('../../../datasets/8labels.csv')

# # Extract texts and labels
# texts = data['text'].tolist()
# labels = data['label'].tolist()

# Define categories
categories = [
    "Personal & Lifestyle",
    "Work & Business",
    "Education & Learning",
    "Financial & Legal",
    "Health & Medical",
    "Travel & Leisure",
    "Entertainment & Media",
    "Utilities & Miscellaneous",
]

# Define label mapping dynamically
# label_mapping = {category: i for i, category in enumerate(categories)}
# y = np.array([label_mapping.get(label, -1) for label in labels])

# # Data preprocessing
# # You may need additional preprocessing steps here such as removing stop words, stemming, or lemmatization.

# # Split data into train and test sets
# train_texts, test_texts, train_labels, test_labels = train_test_split(texts, y, test_size=0.1, random_state=42)

# # Tokenize and encode the text data using DistilBERT tokenizer
# tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
# train_encodings = tokenizer(train_texts, truncation=True, padding=True)
# test_encodings = tokenizer(test_texts, truncation=True, padding=True)

# # Create TensorDatasets
# train_dataset = TensorDataset(torch.tensor(train_encodings['input_ids']),
#                               torch.tensor(train_encodings['attention_mask']),
#                               torch.tensor(train_labels))

# test_dataset = TensorDataset(torch.tensor(test_encodings['input_ids']),
#                              torch.tensor(test_encodings['attention_mask']),
#                              torch.tensor(test_labels))

# # Define batch size
# batch_size = 32

# # Create DataLoaders
# train_dataloader = DataLoader(train_dataset, sampler=RandomSampler(train_dataset), batch_size=batch_size)
# test_dataloader = DataLoader(test_dataset, batch_size=batch_size)

# # Load pre-trained DistilBERT model for sequence classification
# model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=len(categories))

# # Define optimizer and scheduler
# optimizer = TorchAdamW(model.parameters(), lr=2e-5)
# scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.9)

# # Define training parameters
# num_epochs = 4
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model.to(device)

# # Train the model
# for epoch in range(num_epochs):
#     print(f'Epoch {epoch + 1}/{num_epochs}')
#     model.train()
#     total_loss = 0
#     for batch in train_dataloader:
#         batch = tuple(t.to(device) for t in batch)
#         inputs = {'input_ids': batch[0],
#                   'attention_mask': batch[1],
#                   'labels': batch[2]}
#         optimizer.zero_grad()
#         outputs = model(**inputs)
#         loss = outputs.loss
#         total_loss += loss.item()
#         loss.backward()
#         optimizer.step()
#     print(f'Training loss: {total_loss/len(train_dataloader)}')

#     # Optionally, apply learning rate scheduler
#     scheduler.step()

# # Evaluate the model
# model.eval()
# predictions = []
# true_labels = []

# for batch in test_dataloader:
#     batch = tuple(t.to(device) for t in batch)
#     inputs = {'input_ids': batch[0],
#               'attention_mask': batch[1]}
#     with torch.no_grad():
#         outputs = model(**inputs)
#     logits = outputs.logits
#     batch_predictions = logits.argmax(dim=1).cpu().numpy()
#     predictions.extend(batch_predictions)
#     true_labels.extend(batch[2].cpu().numpy())

# # Calculate evaluation metrics
# accuracy = accuracy_score(true_labels, predictions)
# precision = precision_score(true_labels, predictions, average='macro')
# recall = recall_score(true_labels, predictions, average='macro')
# f1 = f1_score(true_labels, predictions, average='macro')

# print(f'Test Accuracy: {accuracy}')
# print(f'Precision: {precision}')
# print(f'Recall: {recall}')
# print(f'F1 Score: {f1}')

# # save model
# tokenizer.save_pretrained("./saved.model/tokenizer")
# model.save_pretrained("./saved.model/")
# print("Model and tokenizer saved successfully.")

# load model
loaded_tokenizer = DistilBertTokenizer.from_pretrained("./saved.model/tokenizer")
loaded_model = DistilBertForSequenceClassification.from_pretrained("./saved.model")

def predict_labels(model, tokenizer, sentences, categories):
    # Move model to appropriate device (CPU or GPU)
    device = next(model.parameters()).device  # Get device of the model
    model.to(device)

    # Encode sentences and move tensors to the same device as the model
    encoded_sentences = tokenizer(sentences, padding=True, truncation=True, max_length=128, return_tensors='pt')
    input_ids = encoded_sentences['input_ids'].to(device)
    attention_masks = encoded_sentences['attention_mask'].to(device)

    # Perform inference on the model
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_masks)
    logits = outputs.logits

    # Move logits to CPU for post-processing
    logits = logits.cpu()

    # Obtain predicted class indices and map them to labels
    predicted_class_indices = logits.argmax(dim=1).tolist()
    # label_mapping = {category: i for i, category in enumerate(categories)}
    reverse_label_mapping = {v: k for k, v in {category: i for i, category in enumerate(categories)}.items()}
    predicted_labels = [reverse_label_mapping[index] for index in predicted_class_indices]

    return predicted_labels

# Define sentences
sentences = [
  # # // Personal & Lifestyle
  # "I just finished reading a fascinating novel. It's amazing how a good book can transport you to another world.",
  # "Spent the afternoon gardening and it was so therapeutic. Nature has a way of calming the mind.",
  # "Today I tried a new recipe for dinner and it turned out delicious! Cooking is such a fun and creative outlet.",
  # "Took some time to meditate this morning. It's important to prioritize mental health and mindfulness.",
  # "Binge-watched my favorite TV show all weekend. Sometimes you just need a little escapism.",

  # # // Work & Business
  # "Had a productive meeting with the team today. Excited about the new project we're working on.",
  # "Finished up a big presentation for tomorrow. Hoping it goes well!",
  # "Received positive feedback from a client today. It's always rewarding to know your work is appreciated.",
  # "Spent the day networking at a conference. Met some interesting people in the industry.",
  # "Working late tonight to meet a deadline. The hustle never stops!",

  # # // Education & Learning
  # "Started learning a new language today. It's challenging but exciting!",
  # "Attended a workshop on digital marketing strategies. Always eager to expand my skillset.",
  # "Reading up on quantum physics for fun. Always fascinated by the mysteries of the universe.",
  # "Took an online course on photography techniques. Can't wait to put my new skills into practice.",
  # "Volunteered to tutor students in math. It's fulfilling to help others learn and grow.",

  # # // Financial & Legal
  # "Met with a financial advisor to review my investment portfolio. Planning for the future is important.",
  # "Filed my taxes early this year. Feels good to have that task out of the way.",
  # "Consulted with a lawyer about a legal matter. It's always wise to seek professional advice.",
  # "Started a budgeting spreadsheet to track my expenses. Money management is key to financial stability.",
  # "Received a raise at work! Hard work pays off.",

  # // Health & Medical
  # "Went for a run this morning to kickstart the day. Exercise is essential for both physical and mental health.",
  # "Scheduled a check-up with my doctor. Regular health screenings are important for early detection.",
  # "Trying out a new diet plan to improve my eating habits. Health is wealth!",
  # "Practiced yoga before bed to unwind and relax. It's amazing how it helps me sleep better.",
  # "Cut out sugary drinks from my diet. Small changes can lead to big health improvements.",

  # // Travel & Leisure
  # "Planning a weekend getaway to the beach. Can't wait to soak up the sun and relax.",
  # "Booked a spontaneous trip to Paris! Sometimes you just have to seize the moment.",
  # "Hiking in the mountains is my favorite way to disconnect and recharge.",
  # "Visited a new museum in town. Always love exploring art and culture.",
  "Your offer letter for amazon has arrived ",

  # // Entertainment & Media
  "Battery low for system",
  "tarak mehta ka ulta chasma.",
  "world war 3 will be for water.",
  "AMAZON, FLIPKART EMAILS CAN BE FRAUD.",
  "Collect span email from my inbox.",

  # // Utilities & Miscellaneous
  "blood is everywhere.",
  "My blood sugar is low.",
  "Compromise is key for good marriage.",
  "doremon is my favorite show",
  "This is a gold coin from stone age.",
]

# Perform prediction using loaded model and tokenizer
predicted_labels = predict_labels(loaded_model, loaded_tokenizer, sentences, categories)

# Print predicted labels
for sentence, label in zip(sentences, predicted_labels):
    print(f"'{sentence}' - Predicted Label: {label}")
