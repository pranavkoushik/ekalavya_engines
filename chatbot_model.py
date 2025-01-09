import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import json
import pickle
import re

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

class ChatbotModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        self.lemmatizer = WordNetLemmatizer()
        self.intent_labels = None
        self.numeric_features = None

    def preprocess_text(self, text):
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        stop_words = set(stopwords.words('english'))
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
        
        return ' '.join(tokens)

    def extract_numeric_features(self, df):
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        return df[numeric_cols]

    def train(self, dataset_path, epochs=50):
        # Load dataset
        df = pd.read_csv(dataset_path)
        
        # Store numeric column names
        self.numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Prepare text data
        questions = df['question'].apply(self.preprocess_text).values
        text_features = self.vectorizer.fit_transform(questions)
        
        # Prepare numeric features
        numeric_features = self.extract_numeric_features(df)
        scaled_features = self.scaler.fit_transform(numeric_features)
        
        # Combine features
        X = np.hstack([text_features.toarray(), scaled_features])
        
        # Prepare labels
        self.intent_labels = df['intent'].unique()
        intent_map = {intent: idx for idx, intent in enumerate(self.intent_labels)}
        y = df['intent'].map(intent_map).values
        
        # Train model
        self.classifier.fit(X, y)
        
        # Save model and preprocessors
        self.save_model()

    def save_model(self):
        # Save classifier
        with open('chatbot_classifier.pkl', 'wb') as f:
            pickle.dump(self.classifier, f)
        
        # Save vectorizer
        with open('vectorizer.pkl', 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        # Save scaler
        with open('scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save labels and features
        with open('model_config.json', 'w') as f:
            json.dump({
                'intent_labels': self.intent_labels.tolist(),
                'numeric_features': self.numeric_features
            }, f)

    def load_model(self):
        # Load classifier
        with open('chatbot_classifier.pkl', 'rb') as f:
            self.classifier = pickle.load(f)
        
        # Load vectorizer
        with open('vectorizer.pkl', 'rb') as f:
            self.vectorizer = pickle.load(f)
        
        # Load scaler
        with open('scaler.pkl', 'rb') as f:
            self.scaler = pickle.load(f)
        
        # Load labels and features
        with open('model_config.json', 'r') as f:
            config = json.load(f)
            self.intent_labels = np.array(config['intent_labels'])
            self.numeric_features = config['numeric_features']

    def predict(self, question, numeric_data=None):
        # Preprocess question
        processed_question = self.preprocess_text(question)
        text_features = self.vectorizer.transform([processed_question]).toarray()
        
        # Prepare numeric features if provided
        if numeric_data is not None:
            numeric_features = np.array([numeric_data[feature] for feature in self.numeric_features])
            scaled_features = self.scaler.transform(numeric_features.reshape(1, -1))
        else:
            scaled_features = np.zeros((1, len(self.numeric_features)))
        
        # Combine features
        X = np.hstack([text_features, scaled_features])
        
        # Make prediction
        prediction = self.classifier.predict_proba(X)
        intent_idx = np.argmax(prediction)
        confidence = prediction[0][intent_idx]
        
        return self.intent_labels[intent_idx], confidence

if __name__ == "__main__":
    # Example usage
    chatbot = ChatbotModel()
    
    # Train model if needed
    # chatbot.train('path_to_dataset.csv')
    
    # Or load existing model
    chatbot.load_model()
    
    # Make prediction
    question = "What were the total sales last month?"
    intent, confidence = chatbot.predict(question)
    print(f"Intent: {intent}, Confidence: {confidence:.2f}")
